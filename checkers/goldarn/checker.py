#!/usr/bin/env python3

import sys
import hashlib
from checklib import BaseChecker, Status, cquit, rnd_string
from goldarn_lib import CheckMachine, WebSocketHandler
from websocket import WebSocketException


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 15
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except WebSocketException:
            self.cquit(Status.DOWN, "Websocket error", "Websocket error")

    def check(self):
        program, expected_output = self.mch.random_program()
        with self.mch.ws() as ws:
            handler = WebSocketHandler(ws=ws)
            self.mch.init_connection(handler)
            self.mch.test_program(handler, program, expected_output, status=Status.MUMBLE)

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        filename = self.mch.get_filename(rnd_string(32))
        program = self.mch.write_to_file_program(filename, flag, print_ok=True)
        with self.mch.ws() as ws:
            handler = WebSocketHandler(ws=ws)
            self.mch.init_connection(handler)
            self.assert_eq(
                self.mch.run_program(handler, program),
                b"ok",
                "Can't write file",
                Status.MUMBLE,
            )
        self.cquit(Status.OK, hashlib.sha256(filename.encode()).hexdigest(), filename)

    def get(self, flag_id: str, flag: str, vuln: str):
        program = self.mch.read_from_file_program(flag_id, print_contents=True)
        with self.mch.ws() as ws:
            handler = WebSocketHandler(ws=ws)
            self.mch.init_connection(handler)
            self.assert_in(
                flag.encode(),
                self.mch.run_program(handler, program),
                "Can't read flag from file",
                Status.CORRUPT,
            )
        self.cquit(Status.OK)


if __name__ == "__main__":
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
