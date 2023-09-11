import xmlrpc.server
import enum


objects = {}

class Adder:

    def __init__(self, a = 0):
        self.a = a

    def set_b(self, b):
        self.b = b

    def get_add(self):
        return self.a + self.b


class StatusCode(enum.Enum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    ERROR = 110

    def __bool__(self):
        return self.value == self.OK or self.value == self.ERROR

class Checker:
    def check(self, host) -> dict:
        return {'code': 101, 'comment': '', 'latency': 0}

    def put(self, host: str, flag: str, flag_id: str) -> dict:
       return {'code': StatusCode.OK, 'comment': '', 'latency': 0, 'host': host, 'flag': flag, 'flag_id': flag_id}

    def get(self, host: str, flag: str, flag_id: str) -> dict:
        return {'code': StatusCode.OK, 'comment': '', 'latency': 0, 'host': host, 'flag': flag, 'flag_id': flag_id}

def is_primitive(obj):
    if isinstance(obj, (int, float, str, bool)):
        return True
    if isinstance(obj, list):
        for item in obj:
            if not is_primitive(item):
                return False
        return True
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not is_primitive(key) or not is_primitive(value):
                return False
        return True
    return False



def create(classname, *args):
    cls = globals()[classname]
    obj = cls(*args)
    objects[str(id(obj))] = obj
    return str(id(obj))

def call(objid, methodname, *args):
    obj = objects[objid]
    method = getattr(obj, methodname)
    return method(*args)
    




server = xmlrpc.server.SimpleXMLRPCServer(("0.0.0.0", 5001), allow_none=True)
server.register_function(create, "create")
server.register_function(call, "call")
server.serve_forever()