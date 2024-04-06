import pymongo
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, FileResponse, RedirectResponse
import os
import re

app = FastAPI()


API_KEY = os.environ.get("API_KEY")
TEAM_COUNT = int(os.environ.get("TEAM_COUNT"))
VPN_COUNT = int(os.environ.get("PEERS"))
VPN_PER_TEAM = VPN_COUNT / TEAM_COUNT
SERVICES = os.environ.get("SERVICES").split(",")
TEAM_TOKENS = os.environ.get("TEAM_TOKENS").split(",")
FLAG_LIFETIME = int(os.environ.get("FLAG_LIFETIME"))


client = pymongo.MongoClient("mongodb://db:27017/")
db = client["range"]


def get_current_tick():
    return db.ticks.find_one(sort=[("tick", pymongo.DESCENDING)])["tick"]


@app.get("/")
def redirect_docs():
    # Redirect to the documentation
    return RedirectResponse(url="/docs")


@app.get("/hosts")
def get_hosts():
    return list(
        db.hosts.find(
            {}, {"ip": 1, "team_id": 1, "service_id": 1, "service_name": 1, "_id": 0}
        )
    )


@app.get("/scores")
def get_scores(tick: int = -1):
    try:
        max_tick = db.ticks.find_one(sort=[("tick", pymongo.DESCENDING)])["tick"]
        min_tick = db.ticks.find_one(sort=[("tick", pymongo.ASCENDING)])["tick"]
        if tick == -1:
            tick = max_tick
        if tick > max_tick:
            tick = max_tick
        if tick < min_tick:
            tick = min_tick
        tickdata = db.ticks.find_one({"tick": tick}, {"_id": 0})
        tickdata["min_tick"] = min_tick
        tickdata["max_tick"] = max_tick
        return tickdata
    except Exception as e:
        return {}


@app.get("/checks")
def get_checks(skip: int = 0, limit: int = 20):
    return list(
        db.checks.find({}, {"_id": 0, "comment": 0})
        .sort("time", -1)
        .skip(TEAM_COUNT * len(SERVICES) * skip)
        .limit(TEAM_COUNT * len(SERVICES) * limit)
    )


@app.get("/flagids")
def get_flagids():
    current_tick = get_current_tick()
    return list(
        db.flags.find(
            {"tick": {"$gte": current_tick - FLAG_LIFETIME}},
            {
                "service": 1,
                "service_id": 1,
                "team_id": 1,
                "flag_id": 1,
                "tick": 1,
                "_id": 0,
            },
        ).sort({"team_id": 1, "service_id": 1, "tick": -1})
    )


@app.post("/steal")
def steal_flag(flag: str, token: str):
    if token not in TEAM_TOKENS:
        return "error: unauthorized"
    correct = db.flags.find_one({"flag": flag})
    if not correct:
        return "error: invalid"
    stealing_team = TEAM_TOKENS.index(token) + 1
    existing = db.steals.find_one({"flag": flag, "stealing_team": stealing_team})
    if existing:
        return "error: duplicate"
    stealing_team = TEAM_TOKENS.index(token) + 1
    if correct["team_id"] == stealing_team:
        return "error: self"
    current_tick = get_current_tick()
    if current_tick - correct["tick"] > FLAG_LIFETIME:
        return "error: expired"
    db.steals.insert_one(
        {
            "service_id": correct["service_id"],
            "team_id": correct["team_id"],
            "stealing_team": stealing_team,
            "flag_id": correct["flag_id"],
            "flag": flag,
            "flag_tick": correct["tick"],
        }
    )
    return "success"


@app.post("/rename")
def rename_team(name: str, token: str):
    if token not in TEAM_TOKENS:
        return "error: unauthorized"
    team_id = TEAM_TOKENS.index(token) + 1
    name = re.sub(r"[^a-zA-Z0-9\-\._]", "", name)
    db.teams.update_one({"team_id": team_id}, {"$set": {"team_name": name}})
    return "success"


@app.get("/teamdata/{team_token}/rangedata.zip")
def get_team_data(team_token: str):
    # Check if team token is strictly hex characters
    if not all(c in "0123456789abcdef" for c in team_token) or len(team_token) != 32:
        return "invalid-team-token"
    return FileResponse(f"/teamdata/{team_token}.zip")
