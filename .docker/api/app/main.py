from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import os

app = FastAPI()


services = {}

API_KEY = os.environ.get('API_KEY')
TEAM_COUNT = int(os.environ.get('TEAM_COUNT'))
VPN_COUNT = int(os.environ.get('PEERS'))
VPN_PER_TEAM = VPN_COUNT / TEAM_COUNT



@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.get('/service/create')
def create_service(hostname: str, ip: str, status: str = '', api_key: str = ''):
    if api_key != API_KEY:
        return 'create-invalid-api-key'
    if ip == '':
        return 'register-invalid-ip'
    service_id = ''.join(hostname.split('-')[1:])
    if service_id not in services:
        services[service_id] = {}
    team_id = hostname.split('-')[0].strip('team')
    services[service_id][team_id] = {'hostname': hostname, 'ip': ip, 'status': status} 
    return hostname


@app.get('/service/update')
def update_service(hostname: str, status: str = '', api_key: str = ''):
    if api_key != API_KEY:
        return {'result': 'update-invalid-api-key'}
    service_id = ''.join(hostname.split('-')[1:])
    if service_id not in services:
        services[service_id] = {}
    team_id = hostname.split('-')[0].strip('team')
    services[service_id][team_id] = {'hostname': hostname, 'status': status} 
    return {'result': 'success'}


@app.get('/targets')
def get_teams():
    return services
 

@app.get('/vpn/{team_id}/wg{peer_id}.conf', response_class=PlainTextResponse)
def get_vpn(team_id: int, peer_id: int):
    if peer_id > VPN_PER_TEAM:
        return 'invalid-peer-id'
    if team_id > TEAM_COUNT:
        return 'invalid-team-id'
    vpn_id = (TEAM_COUNT * team_id) + peer_id + 1
    with open(f'/vpn/peer{vpn_id}/peer{vpn_id}.conf', 'r') as f:
        return f.read()