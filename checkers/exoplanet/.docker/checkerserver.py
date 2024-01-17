import os
import time
import shlex
import socket
import subprocess
import xmlrpc.server
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



def check(host: str, timeout: int) -> dict:
    start = time.time()
    result = ''
    public = ''
    private = ''
    exitcode = StatusCode.ERROR
    try:
        print("Running python3 checker.py check " + host)
        result = subprocess.check_output("python3 checker.py check " + host, shell=True, timeout=timeout, stderr=subprocess.STDOUT)
        print("Result: " + str(result))
        exitcode = StatusCode.OK
    except subprocess.CalledProcessError as e:
        result = e.stdout
        print("Result: " + str(result))
        exitcode = e.returncode
    except subprocess.TimeoutExpired as e:
        result = e.stdout
        exitcode = StatusCode.ERROR
    except Exception as e:
        exitcode = StatusCode.ERROR
    try:
        result = result.decode('latin-1')
        if len(result.split('\n')) > 1:
            private = result.split('\n')[0]
            public = result.split('\n')[1]
        else:
            public = result
    except:
        pass
    status = {'action': 'check', 'host': host, 'code': int(exitcode), 'comment': public, 'latency': int((time.time() - start) * 1000)}
    print('[CHECK] Status: ' + str(status), flush=True)
    return status

def put(host: str, flag: str, flag_id: str, timeout: int) -> dict:
    start = time.time()
    result = ''
    public = ''
    private = ''
    exitcode = StatusCode.ERROR
    try:
        result = subprocess.check_output("python3 checker.py put " + host + " " + flag_id + " " + flag + " 1", shell=True, timeout=timeout, stderr=subprocess.STDOUT)
        exitcode = StatusCode.OK
    except subprocess.CalledProcessError as e:
        result = e.stdout
        exitcode = e.returncode
    except subprocess.TimeoutExpired as e:
        result = e.stdout
        exitcode = StatusCode.ERROR
    except Exception as e:
        exitcode = StatusCode.ERROR
    try:
        result = result.decode('latin-1')
        if len(result.split('\n')) > 1:
            private = result.split('\n')[0]
            public = result.split('\n')[1]
        else:
            public = result
    except:
        pass
    flag_id = public
    if exitcode == StatusCode.OK:
        public = 'OK'
    status = {'action': 'put', 'host': host, 'code': int(exitcode), 'comment': public, 'latency': int((time.time() - start) * 1000), 'flag': flag, 'flag_id': flag_id, 'private': private}
    print('[PUT] Finished: ' + str(status), flush=True)
    return status

def get(host: str, flag: str, flag_id: str, private: str, timeout: int) -> dict:
    start = time.time()
    result = ''
    public = ''
    private = "'" + private.replace("'", "'\\''") + "'"
    try:
        result = subprocess.check_output("python3 checker.py get " + host + " " + private + " " + flag + " 1", shell=True, timeout=timeout, stderr=subprocess.STDOUT)
        exitcode = StatusCode.OK
    except subprocess.CalledProcessError as e:
        result = e.stdout
        exitcode = e.returncode
    except subprocess.TimeoutExpired as e:
        result = e.stdout
        exitcode = StatusCode.ERROR
    except Exception as e:
        exitcode = StatusCode.ERROR
    try:
        result = result.decode('latin-1')
        if len(result.split('\n')) > 1:
            private = result.split('\n')[0]
            public = result.split('\n')[1]
        else:
            public = result
    except:
        pass
    status = {'action': 'get', 'host': host, 'code': int(exitcode), 'comment': public, 'latency': int((time.time() - start) * 1000), 'flag': flag, 'flag_id': flag_id}
    print('[GET] status: ' + str(status), flush=True)
    return status


# Set up routing correctly
if os.environ.get('GATEWAY'):
    os.system('ip route delete default')
    os.system('ip route add default via ' + os.environ.get('GATEWAY'))

TICK_SECONDS = int(os.environ.get('TICK_SECONDS'))

socket.setdefaulttimeout(TICK_SECONDS)
server = xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 5000), allow_none=True)
server.register_function(check, 'check')
server.register_function(put, 'put')
server.register_function(get, 'get')
server.serve_forever()