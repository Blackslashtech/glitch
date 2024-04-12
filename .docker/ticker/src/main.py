import os
import time
import random
import string
import pymongo
import secrets
import dateutil.parser
import threading
import traceback

from checkerclient import RemoteChecker, StatusCode, Flag


client = pymongo.MongoClient("mongodb://db:27017/")
db = client["range"]

range_initialized = False

TEAM_COUNT = int(os.environ.get("TEAM_COUNT"))
SERVICES = os.environ.get("SERVICES").lower().split(",")
CHECKERS = os.environ.get("CHECKERS").split(",")
TICK_SECONDS = int(os.environ.get("TICK_SECONDS"))
START_TIME = int(dateutil.parser.parse(os.environ.get("START_TIME")).timestamp())
END_TIME = int(dateutil.parser.parse(os.environ.get("END_TIME")).timestamp())
RANDOMIZE_CHECKER_TIMES = os.environ.get("RANDOMIZE_CHECKER_TIMES") != "false"


# Flag format: [A-Z0-9]{31}=
def generate_flag() -> str:
    return (
        "".join(
            secrets.choice(string.ascii_uppercase + string.digits) for _ in range(31)
        )
        + "="
    )


# Flag ID format: [a-z0-9]{32}
def generate_flagid() -> str:
    return "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16)
    )


def init() -> None:
    # Ensure indexes are created
    db.teams.create_index(["team_id"])
    db.services.create_index(["service_id"])
    db.services.create_index(["service_name"])
    db.hosts.create_index(["service_name"])
    db.hosts.create_index(["service_id", "team_id"])
    db.hosts.create_index(["ip"])
    db.checks.create_index(["service_id", "team_id"])
    db.checks.create_index(["service_id", "team_id", "code"])
    db.steals.create_index(["service_id", "team_id"])
    db.hosts.create_index(["tick"])
    host_id = 1
    for i in range(1, len(SERVICES) + 1):
        db.services.insert_one(
            {
                "service_id": i,
                "service_name": CHECKERS[i - 1],
                "status": StatusCode.DOWN.value,
            }
        )
        for j in range(1, TEAM_COUNT + 1):
            ip = "10.100." + str(j) + "." + str(host_id)
            hostname = "team" + str(j) + "-" + SERVICES[i - 1].lower()
            db.hosts.insert_one(
                {
                    "service_name": CHECKERS[i - 1],
                    "service_id": i,
                    "team_id": j,
                    "ip": ip,
                    "hostname": hostname,
                    "score": 0,
                    "scores": [],
                    "sla": 0,
                    "offense": 0,
                    "defense": 0,
                    "failed_checks_1": 0,
                    "failed_checks_2": 0,
                    "failed_checks_3": 0,
                    "flags_gained": 0,
                    "flags_lost": 0,
                }
            )
        if host_id < len(SERVICES) and SERVICES[host_id - 1] != SERVICES[host_id]:
            host_id += 1
    for i in range(1, TEAM_COUNT + 1):
        db.teams.insert_one(
            {
                "team_id": i,
                "score": 0,
                "scores": [],
                "team_name": "Team " + str(i),
                "sla": 0,
                "offense": 0,
                "defense": 0,
            }
        )


def check_callback(result: dict) -> None:
    # print('Callback: ' + str(result), flush=True)
    tick = round((time.time() - START_TIME) // TICK_SECONDS)
    if tick - result["tick"] > 1:
        print("Late callback: " + str(result), flush=True)
    db.checks.insert_one(
        {
            "service": result["service_name"],
            "service_id": int(result["service_id"]),
            "team_id": int(result["host"].split(".")[2]),
            "tick": result["tick"],
            "host": result["host"],
            "action": result["action"],
            "code": result["code"],
            "comment": result["comment"],
            "latency": result["latency"],
        }
    )
    if result["action"] == "put" and result["code"] == int(StatusCode.OK):
        db.flags.insert_one(
            {
                "service": result["service_name"],
                "service_id": int(result["service_id"]),
                "team_id": int(result["host"].split(".")[2]),
                "tick": result["tick"] + 1,
                "host": result["host"],
                "flag": result["flag"],
                "flag_id": result["flag_id"],
                "private": result["private"],
            }
        )


# Run all checks on a service for a given tick
def run_checks(service_id: int, service_name: str, target_ips: list, tick: int) -> None:
    # print('Running checks on ' + service_name + ' for tick ' + str(tick), flush=True)
    # Randomize the order of target_ips
    random.shuffle(target_ips)
    # Generate flag objects to be placed on the targets
    put_flags = [
        Flag(host=target_ip, flag=generate_flag(), flag_id=generate_flagid())
        for target_ip in target_ips
    ]
    # Build the get_flag list from the recently_planted_flags list, mapping the keys to the target_ips
    get_flags = []
    for target_ip in target_ips:
        # Get most recent flag for this service and target_ip
        recent_flags = list(
            db.flags.find({"host": target_ip, "service_id": service_id})
            .sort("tick", -1)
            .limit(1)
        )
        if len(recent_flags) > 0:
            flag = Flag(
                host=target_ip,
                flag=recent_flags[0]["flag"],
                flag_id=recent_flags[0]["flag_id"],
                private=recent_flags[0]["private"],
            )
            get_flags.append(flag)
            # print('GET flag: ' + str(get_flags[-1]), flush=True)
        else:
            get_flags.append(Flag(host=target_ip))
    # Run the checks in parallel
    lock = threading.Lock()
    for target_ip, put_flag, get_flag in zip(
        target_ips.copy(), put_flags.copy(), get_flags.copy()
    ):
        try:
            # def __init__(self, checker: str, service: str, callback, tick: int = 0, randomize: bool = False, ticklen: int = 0) -> None:
            checker = RemoteChecker(
                "10.103.2." + str(service_id),
                service_id,
                service_name,
                check_callback,
                tick,
                RANDOMIZE_CHECKER_TIMES,
                lock,
            )
            threading.Thread(
                target=checker.run_all,
                args=(target_ip, put_flag, get_flag, TICK_SECONDS),
            ).start()
        except OSError:
            print("Failed to connect to checker", flush=True)
            return
        except Exception:
            print("Other error:", flush=True)
            print(traceback.format_exc(), flush=True)
            return


def calculate_scores_simple(tick: int = 0) -> None:
    global range_initialized
    print("Calculating scores", flush=True)
    # Calculate the scores for each team
    if not range_initialized:
        # Check if all checks from the current tick are correct and all checks from the previous tick are correct
        if (
            db.checks.count_documents({"tick": tick, "code": int(StatusCode.OK)})
            == TEAM_COUNT * len(SERVICES) * 3
            and time.time() >= START_TIME
        ):  # and db.checks.count_documents({'tick': tick - 1, 'code': int(StatusCode.OK)}) == TEAM_COUNT * len(SERVICES) * 3:
            db.checks.delete_many()
            range_initialized = True
            print("Range Initialized! Going hot...", flush=True)
            return
        else:
            print("Pending initialization, skipping score calculation...", flush=True)
            # Clear any existing data
            db.checks.delete_many({"tick": tick - 1})
            return
    tickdata = {}
    tickdata["tick"] = tick
    tickdata["teams"] = {}
    tickdata["services"] = {}
    print("Team Service          CHECK PUT GET  ", flush=True)
    for team in db.teams.find():
        team_score = 0
        old_team = db.teams.find_one({"team_id": team["team_id"]})
        team_sla = 0
        team_offense = 0
        team_defense = 0
        tickdata["teams"][str(team["team_id"])] = {"data": {}, "hosts": {}}
        for service in db.services.find():
            # Checks that are OK
            all_service_data = {}
            old_host = db.hosts.find_one(
                {"service_id": service["service_id"], "team_id": team["team_id"]}
            )
            sla_score = db.checks.count_documents(
                {
                    "service_id": service["service_id"],
                    "team_id": team["team_id"],
                    "code": int(StatusCode.OK),
                }
            )
            offense_score = db.steals.count_documents(
                {"service_id": service["service_id"], "stealing_team": team["team_id"]}
            )
            defense_score = db.steals.count_documents(
                {"service_id": service["service_id"], "team_id": team["team_id"]}
            )
            flags_gained = offense_score
            flags_lost = defense_score
            service_score = sla_score + (offense_score - defense_score)
            host_sla_delta = sla_score - old_host["sla"]
            host_offense_delta = offense_score - old_host["offense"]
            host_defense_delta = defense_score - old_host["defense"]
            flags_gained_delta = offense_score - old_host["flags_gained"]
            flags_lost_delta = defense_score - old_host["flags_lost"]
            team_offense += offense_score
            team_defense += defense_score
            team_sla += sla_score
            team_score += service_score
            # check_status = db.checks.find({'service_id': service['service_id'], 'team_id': team['team_id'], 'action': 'check'}).sort('tick', -1).limit(1).get(0, None)
            check_status = db.checks.find_one(
                {
                    "service_id": service["service_id"],
                    "team_id": team["team_id"],
                    "action": "check",
                },
                sort=[("tick", pymongo.DESCENDING)],
            )
            # put_status = db.checks.find({'service_id': service['service_id'], 'team_id': team['team_id'], 'action': 'put'}).sort('tick', -1).limit(1).get(0, None)
            put_status = db.checks.find_one(
                {
                    "service_id": service["service_id"],
                    "team_id": team["team_id"],
                    "action": "put",
                },
                sort=[("tick", pymongo.DESCENDING)],
            )
            # get_status = db.checks.find({'service_id': service['service_id'], 'team_id': team['team_id'], 'action': 'get'}).sort('tick', -1).limit(1).get(0, None)
            get_status = db.checks.find_one(
                {
                    "service_id": service["service_id"],
                    "team_id": team["team_id"],
                    "action": "get",
                },
                sort=[("tick", pymongo.DESCENDING)],
            )
            check_code, put_code, get_code = 105, 105, 105
            comments = []
            status_name = "ok"
            failed_checks_1 = 0
            if check_status is not None:
                check_code = check_status["code"]
            if put_status is not None:
                put_code = put_status["code"]
            if get_status is not None:
                get_code = get_status["code"]
            if (
                check_code == int(StatusCode.OK)
                and put_code == int(StatusCode.OK)
                and get_code == int(StatusCode.OK)
            ):
                comments = ["OK"]
            else:
                if put_code != int(StatusCode.OK):
                    comments.append("PUT flag failed")
                    failed_checks_1 += 1
                    status_name = "flag"
                if get_code != int(StatusCode.OK):
                    comments.append("GET flag failed")
                    failed_checks_1 += 1
                    status_name = "flag"
                if check_code != int(StatusCode.OK):
                    comments.append("SLA check failed")
                    failed_checks_1 += 1
                    status_name = "down"
            comments = ", ".join(comments)
            failed_checks_2 = old_host["failed_checks_1"]
            failed_checks_3 = old_host["failed_checks_2"]
            all_host_data = {
                "score": service_score,
                "scores": old_host["scores"] + [service_score],
                "sla": sla_score,
                "offense": offense_score,
                "defense": defense_score,
                "sla_delta": host_sla_delta,
                "offense_delta": host_offense_delta,
                "defense_delta": host_defense_delta,
                "flags_gained": flags_gained,
                "flags_lost": flags_lost,
                "flags_gained_delta": flags_gained_delta,
                "flags_lost_delta": flags_lost_delta,
                "check_status": check_code,
                "put_status": put_code,
                "get_status": get_code,
                "comments": comments,
                "status_name": status_name,
                "failed_checks_1": failed_checks_1,
                "failed_checks_2": failed_checks_2,
                "failed_checks_3": failed_checks_3,
            }

            db.hosts.update_one(
                {"service_id": service["service_id"], "team_id": team["team_id"]},
                {"$set": all_host_data},
            )
            tickdata["teams"][str(team["team_id"])]["hosts"][
                service["service_name"]
            ] = all_host_data
            print(
                str(team["team_id"]).ljust(4)
                + " "
                + service["service_name"].ljust(17)
                + str(check_code).ljust(6)
                + str(put_code).ljust(4)
                + str(get_code).ljust(4)
                + comments,
                flush=True,
            )
        sla_delta = team_sla - old_team["sla"]
        offense_delta = team_offense - old_team["offense"]
        defense_delta = team_defense - old_team["defense"]
        score_delta = team_score - old_team["score"]
        all_team_data = {
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "score": team_score,
            "scores": old_team["scores"] + [team_score],
            "score_delta": score_delta,
            "sla": team_sla,
            "offense": team_offense,
            "defense": team_defense,
            "sla_delta": sla_delta,
            "offense_delta": offense_delta,
            "defense_delta": defense_delta,
        }
        db.teams.update_one({"team_id": team["team_id"]}, {"$set": all_team_data})
        tickdata["teams"][str(team["team_id"])]["data"] = all_team_data
        print("-----------------------------------")
        # print('  Team ' + str(team['team_id']) + ' tick score: ' + str(team_score), flush=True)
    for service in db.services.find():
        # Find the team that first blooded this service
        first_blood = list(
            db.steals.find({"service_id": service["service_id"]})
            .sort("tick", 1)
            .limit(1)
        )
        first_blood_name = "None"
        if len(first_blood) > 0:
            first_blood_name = db.teams.find_one(
                {"team_id": first_blood[0]["stealing_team"]}
            )["team_name"]
        # Find how many teams have exploited this service (unique team IDs with a steal)
        attackers = db.steals.distinct("team_id", {"service_id": service["service_id"]})
        # Find how many teams have been exploited by this service (unique team IDs with a steal)
        victims = db.steals.distinct(
            "stealing_team", {"service_id": service["service_id"]}
        )
        tickdata["services"][str(service["service_id"])] = {
            "name": service["service_name"],
            "id": service["service_id"],
            "firstblood": first_blood_name,
            "attackers": len(attackers),
            "victims": len(victims),
        }
    sorted_tickdata = {
        "tick": tick,
        "services": tickdata["services"],
        "teams": {},
    }
    scoredata = []
    sorted_teams = {}
    rank = 1
    for key, value in sorted(
        tickdata["teams"].items(),
        key=lambda x: (
            x[1]["data"]["score"] + ((10000 - x[1]["data"]["team_id"]) / 10000)
        ),
        reverse=True,
    ):
        sorted_teams[str(rank)] = value
        rank += 1
    # Sort teams by score, and store them in keys corresponding to their rank
    sorted_tickdata["teams"] = sorted_teams
    db.ticks.update_one({"tick": tick}, {"$set": sorted_tickdata}, upsert=True)


def loop() -> None:
    last_run = time.time()
    tick = 0
    while last_run <= END_TIME + TICK_SECONDS:
        # Wait for the next tick
        while time.time() - last_run < TICK_SECONDS:
            time.sleep(1)
        last_run = time.time()
        tick = round((time.time() - START_TIME) // TICK_SECONDS)
        # Calculate the scores for two ticks ago (to ensure all checks have been completed)
        print("### TICK " + str(tick - 2) + " ###", flush=True)
        calculate_scores_simple(tick - 2)
        # Run checks
        checker_id = 1
        for checker_name in CHECKERS:
            target_ips = db.hosts.find({"service_id": checker_id})
            # Run the checks for this service in a new thread
            try:
                threading.Thread(
                    target=run_checks,
                    args=(
                        checker_id,
                        checker_name,
                        [target_ip["ip"] for target_ip in target_ips],
                        tick,
                    ),
                ).start()
            except Exception as e:
                print("Error: failed to start thread for " + checker_name, flush=True)
            checker_id += 1
        print()


def main() -> None:
    init()
    while time.time() < START_TIME - (TICK_SECONDS * 10):
        time.sleep(1)
    loop()


if __name__ == "__main__":
    main()
