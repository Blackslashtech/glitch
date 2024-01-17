#!/usr/bin/env python3.7

from checklib import *


PORT = 17171


class CheckMachine:
    def __init__(self, checker):
        self.checker = checker
        self.port = PORT

    @property
    def url(self):
        return f'http://{self.checker.host}:{self.port}'

    def health_check(self, session):
        url = self.url

        response = session.get(self.url)

        self.checker.assert_eq(response.status_code, 200, "Can't get the main page")

    def add_star(self, session, star):
        url = f"{self.url}/api/stars/"

        response = session.post(url, json=star)

        obj = self.checker.get_json(response, "Can't add star")
        self.checker.assert_eq(response.status_code, 201, "Can't add star")

        self.checker.assert_eq(type(obj), type({}), 'Incorrect star model')
        self.checker.assert_in('id', obj, 'Incorrect star model')

        for key, value in star.items():
            self.checker.assert_in(key, obj, "Can't add star")
            self.checker.assert_eq(value, obj.get(key), "Can't add star")

        return obj

    def add_planet(self, session, planet):
        url = f'{self.url}/api/planets/'

        response = session.post(url, json=planet)

        obj = self.checker.get_json(response, "Can't add planet")
        self.checker.assert_eq(response.status_code, 201, "Can't add planet")

        self.checker.assert_eq(type(obj), type({}), 'Incorrect planet model')
        self.checker.assert_in('id', obj, 'Incorrect planet model')

        for key, value in planet.items():
            self.checker.assert_in(key, obj, "Can't add planet")
            self.checker.assert_eq(value, obj.get(key), "Can't add planet")
   
        return obj

    def get_star(self, session, star_id, star={}):
        url = f'{self.url}/api/stars/{star_id}'

        response = session.get(url)

        obj = self.checker.get_json(response, "Can't get star")
        self.checker.assert_eq(response.status_code, 200, "Can't get star")

        self.checker.assert_eq(type(obj), type({}), 'Incorrect star model')

        for key, value in star.items():
            self.checker.assert_in(key, obj, "Can't get star")
            self.checker.assert_eq(value, obj.get(key), "Can't get star")

        return obj

    def get_planet(self, session, planet_id, planet={}):
        url = f'{self.url}/api/planets/{planet_id}'

        response = session.get(url)

        obj = self.checker.get_json(response, "Can't get planet")
        self.checker.assert_eq(response.status_code, 200, "Can't get planet")

        self.checker.assert_eq(type(obj), type({}), 'Incorrect planet model')

        for key, value in planet.items():
            self.checker.assert_in(key, obj, "Can't get planet")
            self.checker.assert_eq(value, obj.get(key), "Can't get planet")

        return obj
