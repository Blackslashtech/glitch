import xmlrpc.client
import threading
import secrets
import random
import enum
import time



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
    host = ''
    code = StatusCode.OK
    comment = ''
    latency = 0

    def __init__(self, host = '', code: StatusCode = StatusCode.OK, comment: str = '', latency: int = 0) -> None:
        self.host = host
        self.code = code
        self.comment = comment
        self.latency = latency

    def __dict__(self):
        return {
            'host': self.host,
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
    private = ''

    def __init__(self, host = '', flag: str = '', flag_id: str = '', private: str = '') -> None:
        self.host = host
        self.flag = flag
        self.flag_id = flag_id
        self.private = private

    def __dict__(self):
        return {
            'host': self.host,
            'flag': self.flag,
            'flag_id': self.flag_id,
            'private': self.private
        }
    
    def __str__(self):
        return self.__dict__().__str__()



class RemoteChecker:
    def __init__(self, checker: str, service_id: int, service_name: str, callback, tick: int = 0, randomize: bool = False, lock: threading.Lock = threading.Lock()) -> None:
        self.checker = checker
        self.service_id = service_id
        self.service_name = service_name
        self.callback = callback
        self.randomize = randomize
        self.tick = tick
        self.lock = lock

    def check(self, host: str, timeout: int) -> dict:
        if self.randomize:
            time.sleep(secrets.randbelow(timeout))
        with self.lock:
            server = xmlrpc.client.ServerProxy(f'http://{self.checker}:5000', allow_none=True)
            result = server.check(host, timeout)
            result['service_id'] = self.service_id
            result['service_name'] = self.service_name
            result['tick'] = self.tick
            self.callback(result)
        return result

    def put(self, flag: Flag, timeout: int) -> dict:
        if self.randomize:
            time.sleep(secrets.randbelow(timeout))
        with self.lock:
            server = xmlrpc.client.ServerProxy(f'http://{self.checker}:5000', allow_none=True)
            result = server.put(flag.host, flag.flag, flag.flag_id, timeout)
            result['service_id'] = self.service_id
            result['service_name'] = self.service_name
            result['tick'] = self.tick
            if 'private' not in result:
                result['private'] = ''
            self.callback(result)
        return result

    def get(self, flag: Flag, timeout: int) -> dict:
        if self.randomize:
            time.sleep(secrets.randbelow(timeout))
        with self.lock:
            server = xmlrpc.client.ServerProxy(f'http://{self.checker}:5000', allow_none=True)
            result = server.get(flag.host, flag.flag, flag.flag_id, flag.private, timeout)
            result['service_id'] = self.service_id
            result['service_name'] = self.service_name
            result['tick'] = self.tick
            self.callback(result)
        return result

    def run_all(self, host: str, put_flag: Flag, get_flag: Flag, timeout: int) -> None:
        order = ['check', 'put', 'get']
        random.shuffle(order)
        for action in order:
            if action == 'check':
                self.check(host, timeout//3)
            elif action == 'put':
                self.put(put_flag, timeout//3)
            elif action == 'get':
                self.get(get_flag, timeout//3)

