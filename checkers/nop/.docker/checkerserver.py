import os
import enum
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



class Checker:
    def check(self, host: str, timeout: int) -> dict:
        status = {'action': 'check', 'host': host, 'code': int(StatusCode.OK), 'comment': '', 'latency': 0}
        print(status, flush=True)
        return status

    def put(self, host: str, flag: str, flag_id: str, timeout: int) -> dict:
        status = {'action': 'put', 'host': host, 'code': int(StatusCode.OK), 'comment': '', 'latency': 0, 'flag': flag, 'flag_id': flag_id}
        print(status, flush=True)
        return status

    def get(self, host: str, flag: str, flag_id: str, timeout: int) -> dict:
        status = {'action': 'get', 'host': host, 'code': int(StatusCode.OK), 'comment': '', 'latency':0, 'flag': flag, 'flag_id': flag_id}
        print(status, flush=True)
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
if os.environ.get('GATEWAY_IPV4'):
    os.system('ip route delete default')
    os.system('ip route add default via ' + os.environ.get('GATEWAY_IPV4'))
if os.environ.get('GATEWAY_IPV6'):
    os.system('ip -6 route delete default')
    os.system('ip -6 route add default via ' + os.environ.get('GATEWAY_IPV6'))

# Start the xmlrpc server
server = xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 5000), allow_none=True)
server.register_function(create, 'create')
server.register_function(call, 'call')
server.serve_forever()