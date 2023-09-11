from abc import abstractmethod
import xmlrpc.client, xmlrpc.server
import enum


class StatusCode(enum.Enum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    ERROR = 110

    def __bool__(self):
        return self.value == self.OK or self.value == self.ERROR
    

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
            'code': self.code.value,
            'comment': self.comment,
            'latency': self.latency
        }


class Flag:
    flag = ''
    flag_id = ''
    metadata = {}

    def __init__(self, flag: str = '', flag_id: str = '', metadata: dict = {}) -> None:
        self.flag = flag
        self.flag_id = flag_id
        self.metadata = metadata

    def __dict__(self):
        return {
            'flag': self.flag,
            'flag_id': self.flag_id,
            'metadata': self.metadata
        }


# BaseCheckerAdapter is the base class for all checker adapters
# These adapters are used to provide a standard XMLRPC interface for a variety of checker implementations
class BaseCheckerAdapter:
    def __init__(self, host: str) -> None:
        self.host = host
        self.status = Status()
        # Start the XMLRPC server
        self.server = xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 5000))
        self.server.register_function(self.check, 'check')
        self.server.register_function(self.put, 'put')
        self.server.register_function(self.get, 'get')
        

    # Checks whether the service is up and running correctly
    # Returns a Status object representing the result of the check
    @abstractmethod
    def check(self) -> (Status):
        pass

    # Puts a provided flag on the service
    # Returns a tuple of the Status of the put and the Flag object with the flag_id field filled in and any metadata associated with the flag
    @abstractmethod
    def put(self, flag: Flag) -> (Status, Flag):
        pass

    # Gets a flag from the service
    # Returns a tuple of the Status of the get and the Flag object with the flag field filled in and any metadata associated with the flag
    @abstractmethod
    def get(self, flag: Flag) -> (Status):
        pass


class RemoteChecker:
    def __init__(self, host: str) -> None:
        self.host = host
        self.server = xmlrpc.client.ServerProxy(f'http://{self.host}:5000')

    def check(self) -> (Status):
        return Status(**self.server.check())
    
    def put(self, flag: Flag) -> (Status, Flag):
        return tuple(map(lambda x: x(**self.server.put(flag.__dict__)), (Status, Flag)))
    
    def get(self, flag: Flag) -> (Status):
        if flag == Flag():
            return Status()
        return Status(**self.server.get(flag.__dict__))