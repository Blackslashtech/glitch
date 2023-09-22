#!/usr/bin/env python3

import requests

flagapi = "http://range.strider.one/flagids"

flagids = requests.get(flagapi).json()

for flagid in flagids:
    print(str(flagid['service_id']) + "," + str(flagid['team_id']) + "," + str(flagid['flag_id']))
