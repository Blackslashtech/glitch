import pymongo
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import os

app = FastAPI()


API_KEY = os.environ.get('API_KEY')
TEAM_COUNT = int(os.environ.get('TEAM_COUNT'))
VPN_COUNT = int(os.environ.get('PEERS'))
VPN_PER_TEAM = VPN_COUNT / TEAM_COUNT
SERVICES = os.environ.get('SERVICES').split(',')


client = pymongo.MongoClient('mongodb://db:27017/')
db = client['range']


@app.get('/')
def read_root():
    return {'Hello': 'World'}

@app.get('/hosts')
def get_hosts():
    return list(db.hosts.find())

@app.get('/scores')
def get_scores():
    scores = {}
    for team in db.teams.find():
        scores[team['team_id']] = {}
        scores[team['team_id']]['services'] = {}
        for host in db.hosts.find({'team_id': team['team_id']}):
            scores[team['team_id']]['services'][host['service_name']] = host['score']
        scores[team['team_id']]['total'] = team['score']
    return scores

@app.get('/checks')
def get_checks():
    return list(db.checks.find().sort('time', -1).limit(TEAM_COUNT * len(SERVICES) * 10))

@app.get('/flagids')
def get_flagids():
    return list(db.flags.find({}, {'service': 1, 'service_id': 1, 'team_id': 1, 'flag_id': 1, 'tick': 1}))

@app.post('/steal')
def steal_flag(flag: str, team_id: int):
    correct = db.flags.find_one({'flag': flag})
    if not correct:
        return 'invalid'
    existing = db.steals.find_one({'flag': flag})
    if not existing:
        return 'duplicate'
    db.steals.insert_one({'service_id': correct['service_id'], 'team_id': team_id, 'flag_id': correct['flag_id'], 'flag': flag})
    return 'success'


@app.get('/vpn/{team_id}/wg{peer_id}.conf', response_class=PlainTextResponse)
def get_vpn(team_id: int, peer_id: int):
    if peer_id > VPN_PER_TEAM:
        return 'invalid-peer-id'
    if team_id > TEAM_COUNT:
        return 'invalid-team-id'
    vpn_id = (TEAM_COUNT * (team_id - 1)) + peer_id
    with open(f'/vpn/peer{vpn_id}/peer{vpn_id}.conf', 'r') as f:
        return f.read()