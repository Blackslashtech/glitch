from fastapi import FastAPI
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
def create_service(hostname: str, ip: str, api_key: str = ''):
    if api_key != API_KEY:
        return 'create-invalid-api-key'
    if ip == '':
        return 'register-invalid-ip'
    service_id = ''.join(hostname.split('-')[1:])
    hostname = hostname.split('-')[0].split('team')[1]
    if service_id not in services:
        services[service_id] = {}
    team_id = len(services[service_id])
    services[service_id][team_id] = {'hostname': hostname, 'ip': ip} 
    return hostname


@app.get('/service/update')
def update_service(hostname: str, ip: str, api_key: str = ''):
    if api_key != API_KEY:
        return {'result': 'update-invalid-api-key'}
    if ip == '':
        return {'result': 'register-invalid-ip'}
    service_id = ''.join(hostname.split('-')[1:])
    hostname = hostname.split('-')[0].split('team')[1]
    if service_id not in services:
        services[service_id] = {}
    team_id = len(services[service_id])
    services[service_id][team_id] = {'hostname': hostname, 'ip': ip} 
    return {'result': 'success'}


@app.get('/targets')
def get_teams():
    return services
 

@app.get('/vpn.conf')
def get_vpn(team_id: int, peer_id: int):
    if peer_id > VPN_PER_TEAM:
        return 'invalid-peer-id'
    if team_id > TEAM_COUNT:
        return 'invalid-team-id'
    vpn_id = (TEAM_COUNT * team_id) + peer_id + 1
    with open(f'/vpn/config/peer{vpn_id}/peer{vpn_id}.conf', 'r') as f:
        return f.read()