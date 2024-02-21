import os
import enum
import time
import socket
import requests
import xmlrpc.server
import uuid
import secrets
import string


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


# Check is good!
def check(host: str, timeout: int) -> dict:
    status = {'action': 'check', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0}
    start_time = time.time()
    try:
        response = requests.get(f'http://{host}', timeout=timeout)
        if response.status_code == 200:
            status['code'] = int(StatusCode.OK)
    except Exception as e:
        status['comment'] = str(e)
    status['latency'] = int((time.time() - start_time) * 1000)
    print('[CHECK] Status: ' + str(status), flush=True)
    return status

# Must create. Place the flag as a password?
def put(host: str, flag: str, flag_id: str, timeout: int) -> dict:
    status = {'action': 'put', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0, 'flag': flag, 'flag_id': flag_id}
    start_time = time.time()
    pass_alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(pass_alphabet) for i in range(16))
    try:
        reg_payload = {'username':flag_id, 'password':password ,'comments':flag }
        reg_response = requests.post(f'http://{host}/register.php', data=reg_payload, timeout=timeout, allow_redirects=False)
        if 'Created user' in reg_response.headers['Location']:
            login_payload = {'username':flag_id, 'password':password}
            check_reg_response = requests.post(f'http://{host}/login.php', data=login_payload, timeout=timeout)
            if flag in check_reg_response.text:
                status['code'] = int(StatusCode.OK)
    except Exception as e:
        status['comment'] = str(e)
    status['latency'] = int((time.time() - start_time) * 1000)
    print('[PUT] Status: ' + str(status), flush=True)
    return status

def get(host: str, flag: str, flag_id: str, private: str, timeout: int) -> dict:
    status = {'action': 'get', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency':0, 'flag': flag, 'flag_id': flag_id}
    start_time = time.time()
    try:
        response = requests.get(f'http://{host}/items/{flag_id}', timeout=timeout)
        if response.status_code == 200 and flag in response.text:
            status['code'] = int(StatusCode.OK)
    except Exception as e:
        status['comment'] = str(e)
    status['latency'] = int((time.time() - start_time) * 1000)
    print('[GET] Status: ' + str(status), flush=True)
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
server.register_function(check_image, 'check_image')
server.register_function(check_register_account, 'check_register_account')
server.serve_forever()