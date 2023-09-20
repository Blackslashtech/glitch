import os
import json
import time
import http.server
import socket
import subprocess
import threading
import xmlrpc.server
import enum
from socketserver import ThreadingMixIn


class SimpleThreadedXMLRPCServer(ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_on_close = False

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
        self.server_thread = threading.Thread(target=server.serve_foreve, daemon=True)
        self.server_thread.start()
        self.data = {}

    def get_endpoint(self):
        return f'http://127.0.0.1:{self.port_number}'

    def get_id(self):
        try:
            return str(Handler.data[self.port_number]['flagId'])
        except Exception:
            return ''
        
    def destroy(self):
        self.server_thread.join(0)


class Checker:
    def check(self, host: str, timeout: int) -> dict:
        start = time.time()
        print("[CHECK] Starting against " + host)
        comment = ''
        exitcode = StatusCode.ERROR
        try:
            comment = subprocess.check_output("python3 adapter.py check " + host, shell=True, stderr=subprocess.STDOUT, timeout=timeout)
            exitcode = StatusCode.OK
        except subprocess.CalledProcessError as e:
            comment = e.output
            exitcode = e.returncode
        except subprocess.TimeoutExpired as e:
            comment = e.output
            exitcode = StatusCode.ERROR
        except Exception as e:
            comment = 'exception ' + str(e)
            exitcode = StatusCode.ERROR
        try:
            comment = comment.decode('latin-1')
        except:
            comment = ''
        print("[CHECK] Finished against " + str(host) + " after " + str(int((time.time() - start) * 1000)) + " with exitcode " + str(exitcode))
        status = {'action': 'check', 'host': host, 'code': int(exitcode), 'comment': str(comment), 'latency': int((time.time() - start) * 1000)}
        print('Status: ' + str(status), flush=True)
        return status

    def put(self, host: str, flag: str, flag_id: str, timeout: int) -> dict:
        flag_endpoint = FlagEndpoint()
        start = time.time()
        print("[CHECK] Starting against " + host)
        comment = ''
        exitcode = StatusCode.ERROR
        try:
            comment = subprocess.check_output("python3 adapter.py put " + host + " " + flag + " " + flag_id + " " + flag_endpoint.get_endpoint(), shell=True, stderr=subprocess.STDOUT, timeout=timeout)
            exitcode = StatusCode.OK
        except subprocess.CalledProcessError as e:
            comment = e.output
            exitcode = e.returncode
        except subprocess.TimeoutExpired as e:
            comment = e.output
            exitcode = StatusCode.ERROR
        except Exception as e:
            comment = 'exception ' + str(e)
            exitcode = StatusCode.ERROR
        try:
            comment = comment.decode('latin-1')
        except:
            comment = ''
        flag_endpoint.destroy()
        print("[PUT] Finished against " + str(host) + " after " + str(int((time.time() - start) * 1000)) + " with exitcode " + str(exitcode))
        status = {'action': 'put', 'host': host, 'code': int(exitcode), 'comment': str(comment), 'latency': int((time.time() - start) * 1000), 'flag': flag, 'flag_id': flag_endpoint.get_id()}
        print('Status: ' + str(status), flush=True)
        return status

    def get(self, host: str, flag: str, flag_id: str, timeout: int) -> dict:
        start = time.time()
        print("[CHECK] Starting against " + host)
        comment = ''
        exitcode = StatusCode.ERROR
        try:
            comment = subprocess.check_output("python3 adapter.py get " + host + " " + flag + " " + flag_id, shell=True, stderr=subprocess.STDOUT, timeout=timeout)
            exitcode = StatusCode.OK
        except subprocess.CalledProcessError as e:
            comment = e.output
            exitcode = e.returncode
        except subprocess.TimeoutExpired as e:
            comment = e.output
            exitcode = StatusCode.ERROR
        except Exception as e:
            comment = 'exception ' + str(e)
            exitcode = StatusCode.ERROR
        try:
            comment = comment.decode('latin-1')
        except:
            comment = ''
        print("[GET] Finished against " + str(host) + " after " + str(int((time.time() - start) * 1000)) + " with exitcode " + str(exitcode))
        status = {'action': 'get', 'host': host, 'code': int(exitcode), 'comment': str(comment), 'latency': int((time.time() - start) * 1000), 'flag': flag, 'flag_id': flag_id}
        print('Status: ' + str(status), flush=True)
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
    result = method(*args)
    return result


# Set up routing correctly
if os.environ.get('GATEWAY'):
    os.system('ip route delete default')
    os.system('ip route add default via ' + os.environ.get('GATEWAY'))

TICK_SECONDS = int(os.environ.get('TICK_SECONDS'))

socket.setdefaulttimeout(TICK_SECONDS)
server = SimpleThreadedXMLRPCServer(('0.0.0.0', 5000), allow_none=True)
server.register_function(create, 'create')
server.register_function(call, 'call')
server.serve_forever()