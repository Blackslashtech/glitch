import os
import json
import time
import http.server
import multiprocessing

from checkeradapter import BaseCheckerAdapter, Flag, Status, StatusCode

import src.checker


class Handler(http.server.BaseHTTPRequestHandler):
    data: dict = {}
    
    def do_POST(self):
        # Read the post data as json
        self.data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
        self.send_response(200)
        self.end_headers()


class Checker(BaseCheckerAdapter):
    handler = None

    def __init__(self, host):
        super().__init__(host)
        src.checker.team_ip = self.host
        # Because the checklib expects to send flagids back to a server, we have to run that server locally to avoid needing to modify the checklib
        os.environ['FLAGID_SERVICE'] = 'http://127.0.0.1'
        self.handler = Handler()
        server = http.server.HTTPServer(('127.0.0.1', 80), self.handler)
        server.serve_forever()

    def check(self) -> (Status):
        p = multiprocessing.Process(target=src.checker.check_sla)
        start = time.time()
        p.start()
        p.join()
        status = Status(p.exitcode, '', time.time() - start)
        return status

    def put(self, flag: Flag) -> (Status, Flag):
        src.checker.flag = flag.flag
        p = multiprocessing.Process(target=src.checker.put_flag)
        start = time.time()
        p.start()
        p.join()
        status = Status(p.exitcode, '', time.time() - start)
        try:
            flag.flag_id = self.handler.data['flagId']
            return (status, flag)
        except KeyError:
            status.code = StatusCode.ERROR
            return (status, flag)

    def get(self, flag: Flag) -> (Status):
        p = multiprocessing.Process(target=src.checker.get_flag)
        start = time.time()
        p.start()
        p.join()
        status = Status(p.exitcode, '', time.time() - start)
        return (status, flag)
