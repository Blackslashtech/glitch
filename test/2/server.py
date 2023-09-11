import os
import json
import time
import http.server
import multiprocessing
import threading
import xmlrpc.server
import enum

# Because the checklib expects to send flagids back to a server, we have to run that server locally to avoid needing to modify the checklib
os.environ['FLAGID_SERVICE'] = 'http://127.0.0.1'
os.environ['ACTION'] = 'check'
os.environ['TEAM_ID'] = '0'
os.environ['VULNBOX_ID'] = '0'
os.environ['ROUND'] = '0'

import checker


class StatusCode(enum.Enum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    ERROR = 110

    def __bool__(self):
        return self.value == self.OK or self.value == self.ERROR


class Handler(http.server.BaseHTTPRequestHandler):
    data = {}

    def do_POST(self):
        # Get the request port number
        port_number = self.server.server_port
        # Read the post data as json
        Handler.data[port_number] = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8'))
        self.send_response(200)
        self.end_headers()


class FlagEndpoint:
    port_counter = 6000

    def __init__(self) -> None:
        FlagEndpoint.port_counter += 1
        self.port_number = FlagEndpoint.port_counter
        server = http.server.HTTPServer(('127.0.0.1', self.port_number), Handler)
        self.server_thread = threading.Thread(target=server.serve_forever)
        self.server_thread.start()
        self.data = {}

    def get_endpoint(self):
        return f'http://127.0.0.1:{self.port_number}'

    def get_id(self):
        try:
            return Handler.data[self.port_number]['flagId']
        except Exception:
            return ''



class Checker:
    def __init__(self):
        self.flag_endpoint = FlagEndpoint()
        os.environ['FLAGID_SERVICE'] = self.flag_endpoint.get_endpoint()

    def check(self, host: str) -> dict:
        checker.team_ip = host
        p = multiprocessing.Process(target=checker.check_sla)
        start = time.time()
        p.start()
        p.join()
        status = {'code': 1, 'comment': '', 'latency': time.time() - start}
        print(status)
        return status

    def put(self, host: str, flag: str, flag_id: str) -> dict:
        checker.team_ip = host
        checker.flag = flag
        p = multiprocessing.Process(target=checker.put_flag)
        start = time.time()
        p.start()
        p.join()
        status = {'code': 1, 'comment': '', 'latency': time.time() - start, 'host': host, 'flag': flag, 'flag_id': self.flag_endpoint.get_id()}
        return status

    def get(self, host: str, flag: str, flag_id: str) -> dict:
        checker.team_ip = host
        p = multiprocessing.Process(target=checker.get_flag)
        start = time.time()
        p.start()
        p.join()
        status = {'code': 1, 'comment': '', 'latency': time.time() - start, 'host': host, 'flag': flag, 'flag_id': flag_id}
        print(status)
        return status




objects = {}

def create(classname, *args):
    cls = globals()[classname]
    obj = cls(*args)
    objects[str(id(obj))] = obj
    return str(id(obj))

def call(objid, methodname, *args):
    obj = objects[objid]
    method = getattr(obj, methodname)
    return method(*args)


server = xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 5001))
server.register_function(create, 'create')
server.register_function(call, 'call')
server.serve_forever()