import sys
from enum import Enum
import requests
import os


class Status(Enum):
    OK = 101
    DOWN = 104
    CHECKER_DISABLED = 109
    ERROR = 110


class Action(Enum):
    CHECK_SLA = 'CHECK_SLA'
    PUT_FLAG = 'PUT_FLAG'
    GET_FLAG = 'GET_FLAG'

    def __str__(self):
        return str(self.value)


def get_data():
    data = {
        'action': os.environ['ACTION'],
        'teamId': os.environ['TEAM_ID'],
        'vulnboxId': os.environ['VULNBOX_ID'],
        'round': os.environ['ROUND']
    }

    if data['action'] == Action.PUT_FLAG.name or data['action'] == Action.GET_FLAG.name:
        data['flag'] = os.environ['FLAG']
    else:
        data['flag'] = None

    return data


def quit(exit_code, comment='', debug=''):
    if isinstance(exit_code, Status):
        exit_code = exit_code.value

    print(comment)
    print(debug, file=sys.stderr)
    exit(exit_code)


def post_flag_id(service_id, team_id, flag_id):
    r = requests.post(os.environ['FLAGID_SERVICE'] + '/postFlagId', json={
        'token': os.environ['FLAGID_TOKEN'],
        'serviceId': service_id,
        'teamId': team_id,
        'round': int(os.environ['ROUND']),
        'flagId': flag_id
    })
    r.raise_for_status()
