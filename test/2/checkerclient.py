import xmlrpc.client
import enum


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
    

class Status:
    code = StatusCode.OK
    comment = ''
    latency = 0

    def __init__(self, code: StatusCode = StatusCode.OK, comment: str = '', latency: int = 0) -> None:
        self.code = code
        self.comment = comment
        self.latency = latency

    def __dict__(self):
        return {
            'code': int(self.code),
            'comment': self.comment,
            'latency': self.latency
        }

    def __str__(self) -> str:
        return self.__dict__().__str__()


class Flag:
    host = ''
    flag = ''
    flag_id = ''

    def __init__(self, host = '', flag: str = '', flag_id: str = '') -> None:
        self.host = host
        self.flag = flag
        self.flag_id = flag_id

    def __dict__(self):
        return {
            'host': self.host,
            'flag': self.flag,
            'flag_id': self.flag_id,
        }
    
    def __str__(self):
        return self.__dict__().__str__()



class RemoteChecker:
    def __init__(self, checker: str) -> None:
        self.server = xmlrpc.client.ServerProxy(f'http://{checker}:5001')
        self.checkerserver = self.server.create('Checker')

    def check(self, host: str) -> (Status):
        result = self.server.call(self.checkerserver, 'check', host)
        return Status(result['code'], result['comment'], result['latency'])

    def put(self, flag: Flag) -> (Status, Flag):
        result = self.server.call(self.checkerserver, 'put', flag.host, flag.flag, flag.flag_id)
        return (Status(result['code'], result['comment'], result['latency']), Flag(result['host'], result['flag'], result['flag_id']))
    
    def get(self, flag: Flag) -> (Status):
        result = self.server.call(self.checkerserver, 'get', flag.host, flag.flag, flag.flag_id)
        return (Status(result['code'], result['comment'], result['latency']), Flag(result['host'], result['flag'], result['flag_id']))