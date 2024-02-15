from typing import Optional

import checklib
from checklib import BaseChecker
import requests

PORT = 8000


class ExplorersLib:
    @property
    def api_url(self):
        return f'http://{self.host}:{self.port}/api'

    def __init__(self, checker: BaseChecker, port=PORT, host=None):
        self.c = checker
        self.port = port
        self.host = host or self.c.host

    def signup(self, session: requests.Session, username: str, password: str):
        resp = session.post(f'{self.api_url}/signup', json={
            'username': username,
            'password': password
        })
        self.c.assert_eq(resp.status_code, 200, 'Failed to signup')
        resp_json = self.c.get_json(resp, 'Failed to signup: invalid JSON')
        return resp_json

    def signin(self, session: requests.Session, username: str, password: str,
               status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.post(f'{self.api_url}/signin', json={
            'username': username,
            'password': password
        })
        self.c.assert_eq(resp.status_code, 200, 'Failed to signin', status=status)
        resp_json = self.c.get_json(resp, 'Failed to signin: invalid JSON')
        return resp_json

    def create_route(self, session: requests.Session, title: str, description: str):
        resp = session.post(f'{self.api_url}/route/create', json={
            'title': title,
            'description': description
        })
        self.c.assert_eq(resp.status_code, 200, 'Failed to create route')
        resp_json = self.c.get_json(resp, 'Failed to create route: invalid JSON')
        self.c.assert_eq(type(resp_json), dict, 'Failed to create route: invalid JSON')
        return resp_json

    def get_route_list(self, session: requests.Session, status: checklib.Status = checklib.Status.MUMBLE):
        resp = session.get(f'{self.api_url}/route')
        self.c.assert_eq(resp.status_code, 200, 'Failed to get route list', status=status)
        resp_json = self.c.get_json(resp, 'Failed to get route list: invalid JSON')
        self.c.assert_eq(type(resp_json), list, 'Failed to get route list: invalid JSON')
        return resp_json

    def get_route(self, session: requests.Session, route_id: str, token: Optional[str] = None,
                  status: checklib.Status = checklib.Status.MUMBLE):
        params = {}
        if token:
            params['token'] = token
        resp = session.get(f'{self.api_url}/route/{route_id}', params=params)
        self.c.assert_eq(resp.status_code, 200, 'Failed to get route', status=status)
        resp_json = self.c.get_json(resp, 'Failed to get route: invalid JSON')
        self.c.assert_eq(type(resp_json), dict, 'Failed to get route: invalid JSON')
        return resp_json

    def update_route(self, session: requests.Session, route_id: str, description: str, points=list[dict],
                     waypoints=list[dict]):
        pld = {
            'description': description,
            'track_points': points,
            'waypoints': waypoints
        }
        resp = session.post(f'{self.api_url}/route/{route_id}/update', json=pld)

        self.c.assert_eq(resp.status_code, 200, 'Failed to update route')
        resp_json = self.c.get_json(resp, 'Failed to update route: invalid JSON')
        self.c.assert_eq(type(resp_json), dict, 'Failed to update route: invalid JSON')
        return resp_json

    def upload_gpx(self, session: requests.Session, route_id: str, file):
        resp = session.post(f'{self.api_url}/route/{route_id}/upload', files={
            'file': file
        })
        self.c.assert_eq(resp.status_code, 200, 'Failed to upload gpx')
        resp_json = self.c.get_json(resp, 'Failed to upload gpx: invalid JSON')
        self.c.assert_eq(type(resp_json), dict, 'Failed to upload gpx: invalid JSON')
        return resp_json
