import os
import enum
import socket
import xmlrpc.server


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



def check(host: str, timeout: int) -> dict:
    status = {'action': 'check', 'host': host, 'code': int(StatusCode.OK), 'comment': '', 'latency': 0}
    print(status, flush=True)
    return status

def put(host: str, flag: str, flag_id: str, timeout: int) -> dict:
    status = {'action': 'put', 'host': host, 'code': int(StatusCode.OK), 'comment': '', 'latency': 0, 'flag': flag, 'flag_id': flag_id}
    print(status, flush=True)
    return status

def get(host: str, flag: str, flag_id: str, private: str, timeout: int) -> dict:
    status = {'action': 'get', 'host': host, 'code': int(StatusCode.OK), 'comment': '', 'latency':0, 'flag': flag, 'flag_id': flag_id}
    print(status, flush=True)
    return status



# Set up routing correctly
if os.environ.get('GATEWAY'):
    os.system('ip route delete default')
    os.system('ip route add default via ' + os.environ.get('GATEWAY'))

# Start the xmlrpc server
socket.setdefaulttimeout(600)
server = xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 5000), allow_none=True, logRequests=False)
server.register_function(check, 'check')
server.register_function(put, 'put')
server.register_function(get, 'get')
server.serve_forever()