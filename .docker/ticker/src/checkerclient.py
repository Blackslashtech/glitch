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
    flag = ''
    flag_id = ''

    def __init__(self, flag: str = '', flag_id: str = '') -> None:
        self.flag = flag
        self.flag_id = flag_id

    def __dict__(self):
        return {
            'flag': self.flag,
            'flag_id': self.flag_id,
        }
    
    def __str__(self):
        return self.__dict__().__str__()



class RemoteChecker:
    def __init__(self, checker: str, host, callback, tick: int = 0, randomize: bool = False, lock: threading.Lock = threading.Lock()) -> None:
        self.checker = checker
        self.host = host
        self.callback = callback
        self.randomize = randomize
        self.tick = tick
        self.lock = lock

    def check(self, timeout: int) -> dict:
        if self.randomize:
            time.sleep(secrets.randbelow(timeout))
        with self.lock:
            server = xmlrpc.client.ServerProxy(f'http://{self.checker}:5000', allow_none=True)
            result = server.check(self.host['ip'], timeout)
            result['host'] = self.host
            result['tick'] = self.tick
            self.callback(result)
        return result

    def put(self, flag: Flag, timeout: int) -> dict:
        if self.randomize:
            time.sleep(secrets.randbelow(timeout))
        with self.lock:
            server = xmlrpc.client.ServerProxy(f'http://{self.checker}:5000', allow_none=True)
            result = server.put(self.host['ip'], flag.flag, flag.flag_id, timeout)
            result['host'] = self.host
            result['tick'] = self.tick
            self.callback(result)
        return result

    def get(self, flag: Flag, timeout: int) -> dict:
        if self.randomize:
            time.sleep(secrets.randbelow(timeout))
        with self.lock:
            server = xmlrpc.client.ServerProxy(f'http://{self.checker}:5000', allow_none=True)
            result = server.get(self.host['ip'], flag.flag, flag.flag_id, timeout)
            result['host'] = self.host
            result['tick'] = self.tick
            self.callback(result)
        return result

    def run_all(self, put_flag: Flag, get_flag: Flag, timeout: int) -> None:
        order = ['check', 'put', 'get']
        random.shuffle(order)
        for action in order:
            if action == 'check':
                self.check(timeout//3)
            elif action == 'put':
                self.put(put_flag, timeout//3)
            elif action == 'get':
                self.get(get_flag, timeout//3)
