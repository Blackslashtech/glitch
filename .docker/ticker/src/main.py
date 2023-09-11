import os
import time
import random
import string
import pymongo
import dateutil.parser
import multiprocessing
import threading

from checkerclient import RemoteChecker, Status, StatusCode, Flag


client = pymongo.MongoClient('mongodb://db:27017/')
db = client['range']

checkers = {}
checker_results = {}
recently_planted_flags = {}

TEAM_COUNT = int(os.environ.get('TEAM_COUNT'))
SERVICES = os.environ.get('SERVICES').lower().split(',')
TICK_SECONDS = int(os.environ.get('TICK_SECONDS'))
START_TIME = int(dateutil.parser.parse(os.environ.get('START_TIME')).timestamp())
END_TIME = int(dateutil.parser.parse(os.environ.get('END_TIME')).timestamp())
RANDOMIZE_CHECKER_TIMES = os.environ.get('RANDOMIZE_CHECKER_TIMES') != 'false'

# Flag format: [A-Z0-9]{31}=
def generate_flag() -> str:
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(31)) + '='

# Flag ID format: [a-z0-9]{32}
def generate_flagid() -> str:
    return  ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))


def init() -> None:
    # Clear any existing data
    db.teams.delete_many({})
    db.services.delete_many({})
    db.hosts.delete_many({})
    db.checks.delete_many({})
    db.flags.delete_many({})
    db.steals.delete_many({})
    db.teams.create_index(['team_id'])
    db.services.create_index(['service_id'])
    db.services.create_index(['service_name'])
    db.hosts.create_index(['service_name'])
    db.hosts.create_index(['service_id', 'team_id'])
    db.hosts.create_index(['ip'])
    db.checks.create_index(['service_id', 'team_id'])
    db.steals.create_index(['service_id', 'team_id'])
    for i in range(1, len(SERVICES) + 1):
        db.services.insert_one({'service_id': i, 'service_name': SERVICES[i-1], 'status': StatusCode.DOWN.value})
        recently_planted_flags[SERVICES[i-1]] = {}
        for j in range(1, TEAM_COUNT + 1):
            ip = '10.100.' + str(j) + '.' + str(i)
            hostname = 'team' + str(j) + '-' + SERVICES[i-1].lower()
            db.hosts.insert_one({'service_name': SERVICES[i-1], 'service_id': i, 'team_id': j, 'ip': ip, 'hostname': hostname, 'score': 0})
    for i in range(1, TEAM_COUNT + 1):
        db.teams.insert_one({'team_id': i, 'score': 0})
    checker_results['check'] = {}
    checker_results['put'] = {}
    checker_results['get'] = {}

def check_callback(result: dict) -> None:
    global checker_results
    if result is None or 'host' not in result or 'action' not in result:
        return
    target_ip = result['host']
    action = result['action']
    checker_results[action][target_ip] = result

# Run all checks on a service for a given tick
def run_checks(service_name: str, target_ips: list, tick: int) -> None:
    global checker_results, recently_planted_flags
    print("Running checks on " + service_name + " for tick " + str(tick), flush=True)
    service_id = target_ips[0].split('.')[3]
    # Randomize the order of target_ips
    random.shuffle(target_ips)
    # Generate flag objects to be placed on the targets
    put_flags = [Flag(host=target_ip, flag=generate_flag(), flag_id=generate_flagid()) for target_ip in target_ips]
    # Build the get_flag list from the recently_planted_flags list, mapping the keys to the target_ips
    get_flags = []
    for target_ip in target_ips:
        if target_ip in recently_planted_flags[service_name]:
            get_flags.append(recently_planted_flags[service_name][target_ip])
        else:
            get_flags.append(Flag(host=target_ip))
    timeout = TICK_SECONDS//3
    # Run the checks in parallel
    if (RANDOMIZE_CHECKER_TIMES):
        time.sleep(random.randint(0, timeout))
    for target_ip in target_ips:
        try:
            checker = RemoteChecker('10.103.2.' + service_id, check_callback)
        except OSError:
            print('Failed to connect to checker')
            return
        threading.Thread(target=checker.check, args=(target_ip,timeout)).start()
    if (RANDOMIZE_CHECKER_TIMES):
        time.sleep(random.randint(0, timeout))
    for put_flag in put_flags:
        try:
            checker = RemoteChecker('10.103.2.' + service_id, check_callback)
        except OSError:
            print('Failed to connect to checker')
            return
        threading.Thread(target=checker.put, args=(put_flag,timeout)).start()
    if (RANDOMIZE_CHECKER_TIMES):
        time.sleep(random.randint(0, timeout))
    for get_flag in get_flags:
        try:
            checker = RemoteChecker('10.103.2.' + service_id, check_callback)
        except OSError:
            print('Failed to connect to checker')
            return
        threading.Thread(target=checker.get, args=(get_flag,timeout)).start()

    # Wait for half a tick length to pass before checking the results
    time.sleep(TICK_SECONDS/2)

    # Update the database with the check results
    for target_ip in target_ips:
        check_result = checker_results['check'].get(target_ip, {'action': 'check', 'host': target_ip, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0})
        put_result = checker_results['put'].get(target_ip,  {'action': 'put', 'host': target_ip, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0, 'flag': '', 'flag_id': ''})
        get_result = checker_results['get'].get(target_ip,  {'action': 'get', 'host': target_ip, 'code': int(StatusCode.DOWN), 'comment': '', 'latency': 0, 'flag': '', 'flag_id': ''})
        if put_result['flag'] != '':
            recently_planted_flags[service_name][target_ip] = Flag(target_ip, put_result['flag'], put_result['flag_id'])
        db.flags.insert_one({'service': service_name, 'service_id': int(service_id), 'team_id': target_ip.split('.')[3], 'tick': tick + 1, 'host': target_ip, 'flag': put_result['flag'], 'flag_id':  put_result['flag_id']})
        db.checks.insert_one({'service': service_name, 'service_id': int(service_id), 'team_id': int(target_ip.split('.')[3]), 'tick': tick, 'host': target_ip, 'action': 'check', 'host': check_result['host'], 'code': check_result['code'], 'comment': check_result['comment'], 'latency': check_result['latency']})
        db.checks.insert_one({'service': service_name, 'service_id': int(service_id), 'team_id': int(target_ip.split('.')[3]), 'tick': tick, 'host': target_ip, 'action': 'put', 'host': put_result['host'], 'code': put_result['code'], 'comment': put_result['comment'], 'latency': put_result['latency']})
        db.checks.insert_one({'service': service_name, 'service_id': int(service_id), 'team_id': int(target_ip.split('.')[3]), 'tick': tick, 'host': target_ip, 'action': 'get', 'host': get_result['host'], 'code': get_result['code'], 'comment': get_result['comment'], 'latency': get_result['latency']})


# Scoring formulas:
#   team_score = sum(service_scores)
#   service_score = good_checks + flags_stolen

def calculate_scores() -> None:
    print("Calculating scores", flush=True)
    # Calculate the scores for each team
    for team in db.teams.find():
        team_score = 0
        for service in db.services.find():
            # Checks that are OK or ERROR
            # print("Calculating score for team " + str(team['team_id']) + " on service " + service['service_id'], flush=True)
            good_checks = db.checks.count_documents({'service_id': service['service_id'], 'team_id': team['team_id'], 'code': int(StatusCode.OK)})
            # print("Good checks: " + str(good_checks), flush=True)
            flags_stolen = db.steals.count_documents({'service_id': service['service_id'], 'team_id': team['team_id']})
            service_score = good_checks + flags_stolen
            team_score += service_score
            db.hosts.update_one({'service_id': service['service_id'], 'team_id': team['team_id']}, {'$set': {'score': service_score}})
        print("Team " + str(team['team_id']) + " score: " + str(team_score), flush=True)
        db.teams.update_one({'team_id': team['team_id']}, {'$set': {'score': team_score}})


def loop() -> None:
    last_run = 0
    while time.time() < END_TIME:
        # Wait for the next tick
        while time.time() - last_run < TICK_SECONDS:
            time.sleep(1)
        last_run = time.time()
        tick = round((time.time() - START_TIME) // TICK_SECONDS)
        # Run checks
        for service in SERVICES:
            target_ips = db.hosts.find({'service_name': service})
            # Run the checks for this service in a new subprocess
            threading.Thread(target=run_checks, args=(service, [target_ip['ip'] for target_ip in target_ips], tick)).start()
        # Calculate the scores for this tick
        calculate_scores()


def main() -> None:
    init()
    while time.time() < START_TIME:
        time.sleep(1)
    loop()


if __name__ == '__main__':
    main()