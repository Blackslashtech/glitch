#!/usr/bin/env python3

import random
import secrets
import sys
import uuid
import json

import grpc
from checklib import *

from oilmarket_lib import CheckMachine


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 15
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.c = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except self.get_check_finished_exception():
            raise
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                self.cquit(Status.DOWN, "unavailable", f"grpc error: {e}")
            else:
                self.cquit(Status.MUMBLE, f"grpc error: {e.code()}", f"grpc error: {e}")
        except ConnectionRefusedError:
            self.cquit(Status.DOWN, "Connection refused", "Connection refused")

    def check(self):
        with self.c.connect() as channel, self.c.handle_grpc_error(status=Status.MUMBLE):
            stub = self.c.get_stub(channel)

            attesters = [rnd_username() for _ in range(random.randint(2, 7))]
            attester_api_keys = [(attester, self.c.create_attester(stub, attester)) for attester in attesters]

            buyer = rnd_username()
            fake_flag = rnd_string(32)
            buyer_api_key = self.c.create_buyer(stub, buyer, fake_flag, attesters)

            seller = rnd_username()
            seller_api_key = self.c.create_seller(stub, seller)

            barrel_ids = [self.c.add_barrel(stub, seller_api_key) for _ in range(2, 7)]
            random.shuffle(barrel_ids)
            for barrel_id in barrel_ids:
                attester, attester_api_key = random.choice(attester_api_keys)

                request = json.dumps({"barrel_id": barrel_id}).encode()
                signature = self.c.sign(stub, attester_api_key, request)
                service_flag = self.c.sell(stub, seller_api_key, buyer, attester, request, signature)
                self.assert_eq(service_flag, fake_flag, "incorrect data on sell", Status.MUMBLE)

                

            self.cquit(Status.OK)


    def put(self, flag_id: str, flag: str, vuln: str):
        with self.c.connect() as channel, self.c.handle_grpc_error(status=Status.MUMBLE):
            stub = self.c.get_stub(channel)

            attester = rnd_username()
            attester_api_key = self.c.create_attester(stub, attester)
            buyer = rnd_username()
            buyer_api_key = self.c.create_buyer(stub, buyer, flag, [attester])
            self.cquit(Status.OK, 
                       json.dumps({
                           "buyer": buyer,
                           "attester": attester
                       }),
                       json.dumps({
                           "buyer": {"name" : buyer, "api_key": buyer_api_key},
                           "attester": {"name": attester, "api_key": attester_api_key},
                       }),
                       )


    def get(self, flag_id: str, flag: str, vuln: str):
        with self.c.connect() as channel, self.c.handle_grpc_error(status=Status.CORRUPT):
            stub = self.c.get_stub(channel)

            flag_data = json.loads(flag_id)

            buyer = flag_data["buyer"]["name"]
            attester = flag_data["attester"]["name"]
            attester_api_key = flag_data["attester"]["api_key"]

            seller = rnd_username()
            seller_api_key = self.c.create_seller(stub, seller)

            barrel_id = self.c.add_barrel(stub, seller_api_key)

            request = json.dumps({"barrel_id": barrel_id}).encode("ascii")

            signature = self.c.sign(stub, attester_api_key, request)

            service_flag = self.c.sell(stub, seller_api_key, buyer, attester, request, signature)
            self.assert_eq(service_flag, flag, "incorrect flag", Status.CORRUPT)

            self.cquit(Status.OK)



if __name__ == "__main__":
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
