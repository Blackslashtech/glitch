import pymongo
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, FileResponse
import os

import faust

app = FastAPI()


API_KEY = os.environ.get('API_KEY')
TEAM_COUNT = int(os.environ.get('TEAM_COUNT'))
VPN_COUNT = int(os.environ.get('PEERS'))
VPN_PER_TEAM = VPN_COUNT / TEAM_COUNT
SERVICES = os.environ.get('SERVICES').split(',')
TEAM_TOKENS = os.environ.get('TEAM_TOKENS').split(',')
FLAG_LIFETIME = int(os.environ.get('FLAG_LIFETIME'))


client = pymongo.MongoClient('mongodb://db:27017/')
db = client['range']


faust.run()


@app.get('/')
def hello():
    return {'Hello': 'World'}

@app.get('/teams.json')
def get_hosts():
    data = {}
    data['teams'] = []
    data['flag_ids'] = {}
    teams = list(db.teams.find({}, {'_id': 0}))
    services = list(db.services.find({}, {'_id': 0}))
    flags = list(db.flags.find({}, {'_id': 0}))
    for team in teams:
        data['teams'].append(team['team_id'])
    data['flag_ids'] = {}
    for service in services:
        data['flag_ids'][service['service_name']] = {}
        for team in teams:
            data['flag_ids'][service['service_name']][team['team_id']] = []
            for flag in [flag for flag in flags if flag['service_id'] == service['service_id'] and flag['team_id'] == team['team_id']]:
                data['flag_ids'][service['service_name']][team['team_id']].append(flag['flag_id'])
    return data

@app.get('/scores')
def get_scores():
    scores = {}
    for team in list(db.teams.find({}, {'team_id': 1, 'score': 1, '_id': 0})):
        scores[team['team_id']] = {}
        scores[team['team_id']]['services'] = {}
        for host in list(db.hosts.find({'team_id': team['team_id']}, {'service_name': 1, 'score': 1})):
            scores[team['team_id']]['services'][host['service_name']] = host['score']
        scores[team['team_id']]['total'] = team['score']
    return scores

@app.get('/checks')
def get_checks(skip: int = 0, limit: int = 20):
    return list(db.checks.find({}, {'_id': 0, 'comment': 0}).sort('time', -1).skip(TEAM_COUNT * len(SERVICES) * skip).limit(TEAM_COUNT * len(SERVICES) * limit))

@app.get('/flagids')
def get_flagids():
    return list(db.flags.find({}, {'service': 1, 'service_id': 1, 'team_id': 1, 'flag_id': 1, 'tick': 1, '_id': 0}).sort('tick', -1).limit(TEAM_COUNT * len(SERVICES) * FLAG_LIFETIME))

@app.post('/steal')
def steal_flag(flag: str, token: str):
    if token not in TEAM_TOKENS:
        return 'error: unauthorized'
    correct = db.flags.find_one({'flag': flag})
    if not correct:
        return 'error: invalid'
    stealing_team = TEAM_TOKENS.index(token) + 1
    existing = db.steals.find_one({'flag': flag, 'stealing_team': stealing_team})
    if existing:
        return 'error: duplicate'
    stealing_team = TEAM_TOKENS.index(token) + 1
    if correct['team_id'] == stealing_team:
        return 'error: self'
    db.steals.insert_one({'service_id': correct['service_id'], 'team_id': correct['team_id'], 'stealing_team': stealing_team, 'flag_id': correct['flag_id'], 'flag': flag})
    return 'success'

@app.get('/teamdata/{team_token}/rangedata.zip')
def get_team_data(team_token: str):
    # Check if team token is strictly hex characters
    if not all(c in '0123456789abcdef' for c in team_token) or len(team_token) != 32:
        return 'invalid-team-token'
    return FileResponse(f'/teamdata/{team_token}.zip')
