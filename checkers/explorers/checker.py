#!/usr/bin/env python3
import random
import re
import string
import sys

import requests
from checklib import *
from checklib import status

import explorers_lib
import gpxhelper


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 15
    uses_attack_data: bool = True

    req_ua_agents = ['python-requests/2.{}.0'.format(x) for x in range(15, 28)]

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.gpx_helper = gpxhelper.TrackHelper()
        self.lib = explorers_lib.ExplorersLib(self)
        self.id_regexp = re.compile(r'^[0-9A-Za-z]{1,40}$')

    def session_with_req_ua(self):
        sess = get_initialized_session()
        if random.randint(0, 1) == 1:
            sess.headers['User-Agent'] = random.choice(self.req_ua_agents)
        return sess

    def random_route_name(self):
        return 'Expedition #{}'.format(random.randint(1, 10000))

    def random_description(self, name: str):
        choices = ['how was it', 'report', 'detailed report', 'what we found', 'confidential']
        if random.randint(0, 1) == 1:
            return name + ':' + rnd_string(20)
        return '{}: {}'.format(name, random.choice(choices))

    def validate_rid(self, mid):
        self.assert_eq(bool(self.id_regexp.fullmatch(mid)), True, 'Invalid id format')

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

    def check(self):
        session = self.session_with_req_ua()
        username, password = rnd_username(), rnd_password()

        self.lib.signup(session, username, password)
        self.lib.signin(session, username, password)

        random_name = self.random_route_name()
        random_description = self.random_description(random_name)
        route = self.lib.create_route(session, random_name, random_description)

        route_id = route.get('id')

        self.validate_rid(route_id)
        self.assert_eq(route.get('title'), random_name, 'Failed to create route')
        self.assert_eq(route.get('description'), random_description, 'Failed to create route')

        route_list = self.lib.get_route_list(session)
        self.assert_eq(len(route_list), 1, 'Failed to get route list')
        self.assert_eq(route_list[0].get('title'), random_name, 'Failed to get route list')
        self.assert_eq(route_list[0].get('description'), random_description, 'Failed to get route list')

        wpts = [
            gpxhelper.WaypointParams(
                name='Oil found',
                description='Oil found at {}m'.format(random.randint(100, 1000) / 10)
            ),
            gpxhelper.WaypointParams(
                name='Oil not found',
                description='No oil was found',
            )
        ]
        if random.randint(0, 1) == 1:
            wpts.append(gpxhelper.WaypointParams(
                name='Oil found',
                description='Oil found at {}m'.format(random.randint(100, 1000) / 10)
            ))

        gpx_file = self.gpx_helper.random_gpx_from_ds(username, wpts)

        updated_gpx = self.lib.upload_gpx(session, route_id, gpx_file)
        got_waypoints = updated_gpx.get('waypoints', [])
        got_tracks = updated_gpx.get('track_points', [])

        self.assert_eq(set(x.name for x in wpts), set(x.get('name') for x in got_waypoints), 'Failed to upload gpx')
        self.assert_eq(set(x.description for x in wpts), set(x.get('desc') for x in got_waypoints),
                       'Failed to upload gpx')

        got_waypoints[-1]['name'] = rnd_string(31, alphabet=string.ascii_uppercase + string.digits)
        got_waypoints[-1]['desc'] = rnd_string(31, alphabet=string.ascii_uppercase + string.digits)
        new_description = rnd_string(31, alphabet=string.ascii_uppercase + string.digits)

        self.lib.update_route(session, route_id, new_description, got_tracks, got_waypoints)
        updated_gpx = self.lib.get_route(session, route_id)

        self.assert_eq(updated_gpx.get('description'), new_description, 'Failed to update route')
        self.assert_eq(set(x.get('name') for x in got_waypoints), set(x.get('name') for x in updated_gpx['waypoints']),
                       'Failed to update route')
        self.assert_eq(set(x.get('desc') for x in got_waypoints),
                       set(x.get('desc') for x in updated_gpx['waypoints']),
                       'Failed to update route')

        u2, p2 = rnd_username(), rnd_password()
        s2 = self.session_with_req_ua()
        self.lib.signup(s2, u2, p2)

        gpx_by_token = self.lib.get_route(s2, route_id, updated_gpx.get('share_token'))
        self.assert_eq(gpx_by_token.get('title'), random_name, 'Failed to get route by token')
        self.assert_eq(gpx_by_token.get('description'), new_description, 'Failed to get route by token')
        self.assert_eq(set(x.get('name') for x in got_waypoints), set(x.get('name') for x in gpx_by_token['waypoints']),
                       'Failed to get route by token')
        self.assert_eq(set(x.get('desc') for x in got_waypoints),
                       set(x.get('desc') for x in gpx_by_token['waypoints']),
                       'Failed to get route by token')

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        sess = self.session_with_req_ua()
        u = rnd_username()
        p = rnd_password()

        self.lib.signup(sess, u, p)
        self.lib.signin(sess, u, p)

        name = self.random_route_name()
        description = flag

        route = self.lib.create_route(sess, name, description)
        route_id = route.get('id')

        self.validate_rid(route_id)
        self.assert_eq(route.get('title'), name, 'Failed to create route')
        self.assert_eq(route.get('description'), description, 'Failed to create route')

        wpts = [
            gpxhelper.WaypointParams(
                name='Oil found',
                description='Oil found at {}m'.format(random.randint(100, 1000) / 10)
            ),
        ]

        gpx_file = self.gpx_helper.random_gpx(creator=u, waypoints=wpts, num_points=random.randint(5, 15))
        self.lib.upload_gpx(sess, route_id, gpx_file)

        updated_gpx = self.lib.get_route(sess, route_id)

        self.assert_eq(flag, updated_gpx.get('description'), 'Failed to upload gpx')
        self.assert_eq(name, updated_gpx.get('title'), 'Failed to upload gpx')
        self.assert_eq(set(x.name for x in wpts), set(x.get('name') for x in updated_gpx['waypoints']),
                       'Failed to upload gpx')
        self.assert_eq(set(x.description for x in wpts), set(x.get('desc') for x in updated_gpx['waypoints']),
                       'Failed to upload gpx')

        self.cquit(Status.OK, route_id, f"{u}:{p}:{route_id}")

    def get(self, flag_id: str, flag: str, vuln: str):
        u, p, route_id = flag_id.split(':')
        sess = self.session_with_req_ua()
        self.lib.signin(sess, u, p, status=Status.CORRUPT)

        route = self.lib.get_route(sess, route_id, status=Status.CORRUPT)
        self.assert_eq(route.get('description'), flag, 'Failed to get route', status=Status.CORRUPT)

        route_list = self.lib.get_route_list(sess, status=Status.CORRUPT)
        self.assert_in(flag, [x.get('description') for x in route_list], 'Failed to get route list',
                       status=Status.CORRUPT)

        u, p = rnd_username(), rnd_password()
        new_sess = self.session_with_req_ua()
        self.lib.signup(new_sess, u, p)

        new_sess = self.session_with_req_ua()
        self.lib.signin(new_sess, u, p)

        route = self.lib.get_route(new_sess, route_id, token=route.get('share_token'), status=Status.CORRUPT)
        self.assert_eq(route.get('description'), flag, 'Failed to get route by token', status=Status.CORRUPT)

        self.cquit(Status.OK)


if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception() as e:
        cquit(status.Status(c.status), c.public, c.private)
