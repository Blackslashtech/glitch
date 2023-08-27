from fastapi import FastAPI
import os

app = FastAPI()


services = {}

API_KEY = os.environ.get('API_KEY')



@app.get('/')
def read_root():
    return {'Hello': 'World'}



@app.get('/service/register')
def register_service(service_id: str, ip: str, api_key: str = ''):
    global services
    # if api_key != API_KEY:
    #     return {'message': 'Invalid API Key'}
    if ip == '':
        return 'register-invalid-ip'
    if service_id not in services:
        services[service_id] = []
    team_id = len(services[service_id])
    hostname = 'team' + str(team_id) + '.' + service_id + '.lan'
    services[service_id].append({'team_id': team_id, 'service_id': service_id, 'ip': ip, 'hostname': hostname})
    return hostname


@app.get('/targets')
def get_teams():
    global services
    # Take the 2d array of services/teams and rotate it so that the teams are the outer array
    # and the services are the inner array
    targets = []
    for service_name in services:
        for i in range(len(services[service_name])):
            if len(targets) <= i:
                targets.append([])
            targets[i].append(services[service_name][i])
    return targets
 