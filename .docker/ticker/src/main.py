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


client = pymongo.MongoClient('mongodb://db:27017/')
db = client['range']

range_initialized = False

TEAM_COUNT = int(os.environ.get('TEAM_COUNT'))
SERVICES = os.environ.get('SERVICES').lower().split(',')
TICK_SECONDS = int(os.environ.get('TICK_SECONDS'))
START_TIME = int(dateutil.parser.parse(os.environ.get('START_TIME')).timestamp())
END_TIME = int(dateutil.parser.parse(os.environ.get('END_TIME')).timestamp())
RANDOMIZE_CHECKER_TIMES = os.environ.get('RANDOMIZE_CHECKER_TIMES') != 'false'
IPV6_ENABLED = os.environ.get('IPV6_ENABLED') == 'true'


# Flag format: [A-Z0-9]{31}=
def generate_flag() -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(31)) + '='

# Flag ID format: [a-z0-9]{32}
def generate_flagid() -> str:
    return  ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(16))


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
    db.checks.create_index(['service_id', 'team_id', 'code'])
    db.steals.create_index(['service_id', 'team_id'])
    for service_id in range(2, len(SERVICES) + 2):
        db.services.insert_one({'service_id': service_id, 'service_name': SERVICES[service_id-1], 'status': StatusCode.DOWN.value})
        for team_id in range(2, TEAM_COUNT + 2):
            if IPV6_ENABLED:
                ip = 'fd10:100::' + str(team_id) + ':' + str(service_id)
            else:
                ip = '10.100.' + str(team_id) + '.' + str(service_id)
            hostname = 'team' + str(team_id) + '-' + SERVICES[service_id-1].lower()
            db.hosts.insert_one({'service_name': SERVICES[service_id-1], 'service_id': service_id, 'team_id': team_id, 'ip': ip, 'hostname': hostname, 'score': 0})
    for team_id in range(2, TEAM_COUNT + 2):
        db.teams.insert_one({'team_id': team_id, 'score': 0})

def check_callback(result: dict) -> None:
    # print('Callback: ' + str(result), flush=True)
    tick = round((time.time() - START_TIME) // TICK_SECONDS)
    if tick - result['tick'] > 1:
        print('Late callback: ' + str(result), flush=True)
    db.checks.insert_one({'service': result['service'], 'service_id': int(result['host'].split('.')[3]), 'team_id': int(result['host'].split('.')[2]), 'tick': result['tick'], 'host': result['host'], 'action': result['action'], 'code': result['code'], 'comment': result['comment'], 'latency': result['latency']})
    if result['action'] == 'put' and result['code'] == int(StatusCode.OK):
        db.flags.insert_one({'service':  result['service'], 'service_id': int(result['host'].split('.')[3]), 'team_id': int(result['host'].split('.')[2]), 'tick': result['tick'] + 1, 'host': result['host'], 'flag': result['flag'], 'flag_id':  result['flag_id']})


# Run all checks on a service for a given tick
def run_checks(service_name: str, target_ips: list, tick: int) -> None:
    # print('Running checks on ' + service_name + ' for tick ' + str(tick), flush=True)
    service_id = target_ips[0].split('.')[3]
    # Randomize the order of target_ips
    random.shuffle(target_ips)
    # Generate flag objects to be placed on the targets
    put_flags = [Flag(host=target_ip, flag=generate_flag(), flag_id=generate_flagid()) for target_ip in target_ips]
    # Build the get_flag list from the recently_planted_flags list, mapping the keys to the target_ips
    get_flags = []
    for target_ip in target_ips:
        # Get most recent flag for this service and target_ip
        recent_flags = list(db.flags.find({'host': target_ip}).sort('tick',-1).limit(1))
        if len(recent_flags) > 0:
            get_flags.append(Flag(host=target_ip, flag=recent_flags[0]['flag'], flag_id=recent_flags[0]['flag_id']))
            # print('GET flag: ' + str(get_flags[-1]), flush=True)
        else:
            get_flags.append(Flag(host=target_ip))
    # Run the checks in parallel
    lock = threading.Lock()
    for target_ip, put_flag, get_flag in zip(target_ips.copy(), put_flags.copy(), get_flags.copy()):
        try:
            # def __init__(self, checker: str, service: str, callback, tick: int = 0, randomize: bool = False, ticklen: int = 0) -> None:
            if IPV6_ENABLED:
                checker = RemoteChecker('fd10:103::2:' + service_id, service_name, check_callback, tick, RANDOMIZE_CHECKER_TIMES, lock)
            else:
                checker = RemoteChecker('10.103.2.' + service_id, service_name, check_callback, tick, RANDOMIZE_CHECKER_TIMES, lock)
            threading.Thread(target=checker.run_all, args=(target_ip,put_flag,get_flag,TICK_SECONDS)).start()
        except OSError:
            print('Failed to connect to checker', flush=True)
            return
        except Exception:
            print('Other error:', flush=True)
            print(traceback.format_exc(), flush=True)
            return


def calculate_scores(tick: int = 0) -> None:
    global range_initialized
    print('Calculating scores', flush=True)
    # Calculate the scores for each team
    if not range_initialized:
        # Check if all checks from the current tick are correct
        if db.checks.count_documents({'tick': tick, 'code': int(StatusCode.OK)}) == TEAM_COUNT * len(SERVICES) * 3:
            range_initialized = True
            print('Range Initialized! Going hot...', flush=True)
        else:
            print('Pending initialization, skipping score calculation...', flush=True)
            # Clear any existing data
            db.checks.delete_many({'tick': tick})
            return
    print('Team Service          CHECK PUT GET  ', flush=True)
    for team in db.teams.find():
        team_score = 0
        for service in db.services.find():
            # Checks that are OK or ERROR
            sla_score = db.checks.count_documents({'service_id': service['service_id'], 'team_id': team['team_id'], 'code': int(StatusCode.OK)})
            offense_score = db.steals.count_documents({'service_id': service['service_id'], 'stealing_team': team['team_id']})
            defense_score = db.steals.count_documents({'service_id': service['service_id'], 'team_id': team['team_id']})
            service_score = sla_score + (offense_score - defense_score)
            team_score += service_score
            db.hosts.update_one({'service_id': service['service_id'], 'team_id': team['team_id']}, {'$set': {'score': service_score}})
            check_status = db.checks.find_one({'tick': tick, 'service_id': service['service_id'], 'team_id': team['team_id'], 'action': 'check'})
            put_status = db.checks.find_one({'tick': tick, 'service_id': service['service_id'], 'team_id': team['team_id'], 'action': 'put'})
            get_status = db.checks.find_one({'tick': tick, 'service_id': service['service_id'], 'team_id': team['team_id'], 'action': 'get'})
            check_code, put_code, get_code = 105, 105, 105
            comments = ''
            if check_status is not None:
                check_code = check_status['code']
            if put_status is not None:
                put_code = put_status['code']
            if get_status is not None:
                get_code = get_status['code']
            print(str(team['team_id']).ljust(4) + ' ' + service['service_name'].ljust(17) + str(check_code).ljust(6) + str(put_code).ljust(4) + str(get_code).ljust(4) + comments, flush=True)
        db.teams.update_one({'team_id': team['team_id']}, {'$set': {'score': team_score}})
        print('-----------------------------------')
        # print('  Team ' + str(team['team_id']) + ' tick score: ' + str(team_score), flush=True)


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
        print('### TICK ' + str(tick) + ' ###', flush=True)
        calculate_scores(tick-2)
        # Run checks
        for service in SERVICES:
            target_ips = db.hosts.find({'service_name': service})
            # Run the checks for this service in a new thread
            threading.Thread(target=run_checks, args=(service, [target_ip['ip'] for target_ip in target_ips], tick)).start()
        print()


def main() -> None:
    init()
    while time.time() < START_TIME - (TICK_SECONDS * 3):
        time.sleep(1)
    loop()


if __name__ == '__main__':
    main()