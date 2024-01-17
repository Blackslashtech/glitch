#!/usr/bin/env python3.7

from gevent import monkey
monkey.patch_all()

import os
import sys
import json
import enum
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from exo_lib import *

import generators


class Checker(BaseChecker):
    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.RequestException as e:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

    def check(self):
        session = get_initialized_session()

        self.mch.health_check(session)

        starObj = Checker.generate_star()
        star = self.mch.add_star(session, starObj)

        planetObj1 = Checker.generate_planet(star['id'])
        planetObj2 = Checker.generate_planet(star['id'])
        planet1 = self.mch.add_planet(session, planetObj1)
        planet2 = self.mch.add_planet(session, planetObj2)

        star = self.mch.get_star(session, star['id'], starObj)

        self.assert_in('planets', star, 'Incorrect star model')
        self.assert_in(planet1['id'], star['planets'], "Can't get planet from star")
        self.assert_in(planet2['id'], star['planets'], "Can't get planet from star")
        
        self.mch.get_planet(session, planet1['id'], planetObj1)
        self.mch.get_planet(session, planet2['id'], planetObj2)

        self.cquit(Status.OK)

    def put(self, flag_id, flag, vuln):
        session = get_initialized_session()

        star = self.mch.add_star(session, Checker.generate_star())
        planet = self.mch.add_planet(session, Checker.generate_planet(star['id'], flag))

        self.cquit(Status.OK, star['id'], json.dumps([session.cookies.items(), star['id'], planet['id']]))

    def get(self, flag_id, flag, vuln):
        session = get_initialized_session()

        cookies, star_id, planet_id = json.loads(flag_id)

        star = self.mch.get_star(session, star_id)

        for name, value in cookies:
            session.cookies.set(name, value)

        planet = self.mch.get_planet(session, planet_id)

        self.assert_eq(planet['name'], flag, "Can't get flag", status=Status.CORRUPT)

        self.cquit(Status.OK)

    @staticmethod
    def generate_star():
        return {
            'name': generators.star_name(),
            'location': generators.star_location()
        }

    @staticmethod
    def generate_planet(star_id, flag=None):
        return {
            'starId': star_id,
            'name': flag or generators.planet_name(),
            'location': generators.planet_location(),
            'type': generators.planet_type(),
            'isHidden': flag is not None
        }


if __name__ == '__main__':
    action, hostname, params = sys.argv[1], sys.argv[2], sys.argv[3:]

    checker = Checker(hostname)

    try:
        checker.action(action, *params)
    except checker.get_check_finished_exception():
        cquit(Status(checker.status), checker.public, checker.private)
