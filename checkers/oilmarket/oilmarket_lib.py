import random
import string
import uuid
from typing import Callable, List, NamedTuple

from checklib import *
import grpc
from contextlib import contextmanager
from oilmarket_pb2 import (
    SignRequest,
    SignResponse,
    SellRequest,
    SellResponse,
    CreateAttesterRequest,
    CreateBuyerRequest,
    CreateSellerRequest,
    ApiKeyResponse,
    AddBarrelRequest,
    AddBarrelResponse,
)
from oilmarket_pb2_grpc import OilmarketStub

PORT = 2112

class Buyer(NamedTuple):
    name: str
    attesters: List[str]


class CheckMachine:
    def __init__(self, c: BaseChecker):
        self.c = c
        self.addr = f"{self.c.host}:{PORT}"
        self.conn_pool: list[(OilmarketStub, grpc.Channel)] = []

    def connect(self) -> grpc.Channel:
        channel = grpc.insecure_channel(self.addr)
        return channel

    @staticmethod
    def get_stub(channel): 
        return OilmarketStub(channel)

    @staticmethod
    def sign(
             stub: OilmarketStub,
             api_key: str,
             request: bytes,
             ) -> bytes:
        resp: SignResponse = stub.Sign(
            SignRequest(
                api_key=api_key,
                request=request
            )
        )
        return resp.signature

    @staticmethod
    def sell(
             stub: OilmarketStub,
             api_key: str, 
             buyer: str,
             attester: str,
             request: bytes,
             signature: bytes,
             ) -> str:
        resp: SellResponse = stub.Sell(
            SellRequest(
                api_key=api_key,
                buyer=buyer,
                attester=attester,
                request=request,
                signature=signature,
            )
        )
        return resp.flag

    @staticmethod
    def create_buyer(
                    stub: OilmarketStub,
                    name: str,
                    flag: str,
                    attesters: List[str],
                    ) -> str:
        resp: ApiKeyResponse = stub.CreateBuyer(
            CreateBuyerRequest(
                name=name,
                flag=flag,
                attesters=attesters,
            )
        )
        return resp.api_key

    @staticmethod
    def create_attester(
                       stub: OilmarketStub,
                       name: str,
                       ) -> str:
        resp: ApiKeyResponse = stub.CreateAttester(
            CreateAttesterRequest(
                name=name,
            )
        )
        return resp.api_key

    @staticmethod
    def create_seller(
                     stub: OilmarketStub,
                     name: str,
                     ) -> str:
        resp: ApiKeyResponse = stub.CreateSeller(
            CreateSellerRequest(
                name=name,
            )
        )
        return resp.api_key

    @staticmethod
    def add_barrel(
                  stub: OilmarketStub,
                  api_key: str,
                  ) -> int:
        resp: AddBarrelResponse = stub.AddBarrel(
            AddBarrelRequest(
                api_key=api_key,
            )
        )
        return resp.id


    @contextmanager
    def handle_grpc_error(self, status=Status.MUMBLE):
        try:
            yield
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise
            else:
                self.c.cquit(status, f"grpc error: {e.code()}", f"grpc error: {e}")

    @staticmethod
    def is_uuid(s: str) -> bool:
        try:
            uuid.UUID(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def fake_flag() -> str:
        return (
            "B" + rnd_string(31, alphabet=string.ascii_uppercase + string.digits) + "="
        )

