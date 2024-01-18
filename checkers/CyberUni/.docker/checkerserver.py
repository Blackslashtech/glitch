import os
import json
import time
import http.server
import socket
import subprocess
import threading
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
        self.server_thread = threading.Thread(target=server.handle_request)
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



def check(host: str, timeout: int) -> dict:
    start = time.time()
    comment = ''
    exitcode = StatusCode.ERROR
    try:
        comment = subprocess.check_output("python3 checker.py", shell=True, stderr=subprocess.STDOUT, timeout=timeout, env={"ACTION": "CHECK_SLA", "HOST": host})
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
    status = {'action': 'check', 'host': host, 'code': int(exitcode), 'comment': str(comment), 'latency': int((time.time() - start) * 1000)}
    print('[CHECK] Status: ' + str(status), flush=True)
    return status

def put(host: str, flag: str, flag_id: str, timeout: int) -> dict:
    flag_endpoint = FlagEndpoint()
    start = time.time()
    comment = ''
    exitcode = StatusCode.ERROR
    try:
        comment = subprocess.check_output("python3 checker.py put", shell=True, stderr=subprocess.STDOUT, timeout=timeout, env={"ACTION": "PUT_FLAG", "HOST": host, "FLAG": flag})
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
    status = {'action': 'put', 'host': host, 'code': int(exitcode), 'comment': str(comment), 'latency': int((time.time() - start) * 1000), 'flag': flag, 'flag_id': flag_endpoint.get_id()}
    print('[PUT] Status: ' + str(status), flush=True)
    return status

def get(host: str, flag: str, flag_id: str, private: str, timeout: int) -> dict:
    start = time.time()
    comment = ''
    exitcode = StatusCode.ERROR
    try:
        comment = subprocess.check_output("python3 checker.py", shell=True, stderr=subprocess.STDOUT, timeout=timeout, env={"ACTION": "GET_FLAG", "HOST": host, "FLAG": flag})
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
    status = {'action': 'get', 'host': host, 'code': int(exitcode), 'comment': str(comment), 'latency': int((time.time() - start) * 1000), 'flag': flag, 'flag_id': flag_id}
    print('[GET] Status: ' + str(status), flush=True)
    return status


# Set up routing correctly
if os.environ.get('GATEWAY'):
    os.system('ip route delete default')
    os.system('ip route add default via ' + os.environ.get('GATEWAY'))

TICK_SECONDS = int(os.environ.get('TICK_SECONDS'))

socket.setdefaulttimeout(TICK_SECONDS)
server = xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 5000), allow_none=True, logRequests=False)
server.register_function(check, 'check')
server.register_function(put, 'put')
server.register_function(get, 'get')
server.serve_forever()