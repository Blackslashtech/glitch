import os
import enum
import time
import socket
import requests
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



def check(host: str, timeout: int) -> dict:
    status = {'action': 'check', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0}
    print('Start CHECK: ' + str(status), flush=True)
    # Check if host is an ipv6 address
    if ':' in host:
        host = '[' + host + ']'
    start_time = time.time()
    try:
        response = requests.get(f'http://{host}', timeout=timeout)
        if response.status_code == 200:
            status['code'] = int(StatusCode.OK)
    except Exception as e:
        status['comment'] = str(e)
    status['latency'] = int((time.time() - start_time) * 1000)
    print('End CHECK: ' + str(status), flush=True)
    return status

def put(host: str, flag: str, flag_id: str, timeout: int) -> dict:
    status = {'action': 'put', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0, 'flag': flag, 'flag_id': flag_id}
    print('Start PUT: ' + str(status), flush=True)
    # Check if host is an ipv6 address
    if ':' in host:
        host = '[' + host + ']'
    start_time = time.time()
    try:
        response = requests.post(f'http://{host}/items/{flag_id}/{flag}', timeout=timeout)
        if response.status_code == 200:
            status['code'] = int(StatusCode.OK)
    except Exception as e:
        status['comment'] = str(e)
    status['latency'] = int((time.time() - start_time) * 1000)
    print('End PUT: ' + str(status), flush=True)
    return status

def get(host: str, flag: str, flag_id: str, timeout: int) -> dict:
    status = {'action': 'get', 'host': host, 'code': int(StatusCode.DOWN), 'comment': '', 'latency':0, 'flag': flag, 'flag_id': flag_id}
    print('Start GET: ' + str(status), flush=True)
    # Check if host is an ipv6 address
    if ':' in host:
        host = '[' + host + ']'
    start_time = time.time()
    try:
        response = requests.get(f'http://{host}/items/{flag_id}', timeout=timeout)
        if response.status_code == 200 and flag in response.text:
            status['code'] = int(StatusCode.OK)
    except Exception as e:
        status['comment'] = str(e)
    status['latency'] = int((time.time() - start_time) * 1000)
    print('End GET: ' + str(status), flush=True)
    return status



# Set up routing correctly
if os.environ.get('GATEWAY_IPV4'):
    os.system('ip route delete default')
    os.system('ip route add default via ' + os.environ.get('GATEWAY_IPV4'))
if os.environ.get('GATEWAY_IPV6'):
    os.system('ip -6 route delete default')
    os.system('ip -6 route add default via ' + os.environ.get('GATEWAY_IPV6'))
    os.system('ip -6 neigh add proxy ' +  os.environ.get('GATEWAY_IPV6') + ' dev eth0')

# Start the xmlrpc server
socket.setdefaulttimeout(600)
server = xmlrpc.server.SimpleXMLRPCServer(('0.0.0.0', 5000), allow_none=True)
server.register_function(check, 'check')
server.register_function(put, 'put')
server.register_function(get, 'get')
server.serve_forever()