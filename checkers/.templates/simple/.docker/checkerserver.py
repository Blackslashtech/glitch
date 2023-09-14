import os
import enum
import time
import socket
import requests
import xmlrpc.server
from socketserver import ThreadingMixIn


class SimpleThreadedXMLRPCServer(ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    pass

class StatusCode(enum.Enum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    ERROR = 110

    def __bool__(self):
        return self.value == self.OK or self.value == self.ERROR
    
    def __int__(self):
        return self.value



class Checker:
    def check(self, host: str, timeout: int) -> dict:
        status = {'action': 'check', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0}
        print('Start CHECK: ' + str(status), flush=True)
        start_time = time.time()
        try:
            response = requests.get(f'http://{host}', timeout=timeout)
            if response.status_code == 200:
                status['code'] = int(StatusCode.OK)
        except Exception as e:
            status['comment'] = str(e)
        status['latency'] = int((time.time() - start_time) * 1000)
        print('End CHECK: ' + str(status), flush=True)
        return status

    def put(self, host: str, flag: str, flag_id: str, timeout: int) -> dict:
        status = {'action': 'put', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0, 'flag': flag, 'flag_id': flag_id}
        print('Start PUT: ' + str(status), flush=True)
        start_time = time.time()
        try:
            response = requests.post(f'http://{host}/items/{flag_id}/{flag}', timeout=timeout)
            if response.status_code == 200:
                status['code'] = int(StatusCode.OK)
        except Exception as e:
            status['comment'] = str(e)
        status['latency'] = int((time.time() - start_time) * 1000)
        print('End PUT: ' + str(status), flush=True)
        return status

    def get(self, host: str, flag: str, flag_id: str, timeout: int) -> dict:
        status = {'action': 'get', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency':0, 'flag': flag, 'flag_id': flag_id}
        print('Start GET: ' + str(status), flush=True)
        start_time = time.time()
        try:
            response = requests.get(f'http://{host}/items/{flag_id}', timeout=timeout)
            if response.status_code == 200 and flag in response.text:
                status['code'] = int(StatusCode.OK)
        except Exception as e:
            status['comment'] = str(e)
        status['latency'] = int((time.time() - start_time) * 1000)
        print('End GET: ' + str(status), flush=True)
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


# Set up routing correctly
if os.environ.get('GATEWAY'):
    os.system('ip route delete default')
    os.system('ip route add default via ' + os.environ.get('GATEWAY'))

# Start the xmlrpc server
socket.setdefaulttimeout(600)
server = SimpleThreadedXMLRPCServer(('0.0.0.0', 5000), allow_none=True)
server.register_function(create, 'create')
server.register_function(call, 'call')
server.serve_forever()