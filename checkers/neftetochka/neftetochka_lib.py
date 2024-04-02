import json
import requests
import websocket

from typing import NamedTuple

from checklib import *

PORT = 8087

class Station(NamedTuple):
    id: int
    x: int
    y: int

class Link(NamedTuple):
    id1: int
    id2: int

class User(NamedTuple):
    uid: str
    username: str
    balance: int

class Oil(NamedTuple):
    sender: str
    message: str
    station_id: int


class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}/api'

    @property
    def ws_url(self):
        return f'ws://{self.c.host}:{self.port}/ws/ws'

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.port = PORT

    def get_websocket(self) -> websocket.WebSocket:
        ws = websocket.WebSocket()
        ws.connect(self.ws_url)
        ws.settimeout(7)
        return ws

    def register(self, session: requests.Session, username: str, password: str, status: Status) -> str:
        resp = session.post(f"{self.url}/register", json={"username": username, "password": password})

        resp = self.c.get_json(resp, "Invalid response on register", status)
        self.c.assert_eq(type(resp), dict, "Invalid response on register", status)
        if resp.get("error", "") != "":
            self.c.cquit(status, "Error on register")
        self.c.assert_eq(type(resp.get("id")), str, "Invalid response on register", status)
        self.c.assert_eq(len(resp.get("id")), 0x20, "Invalid response on register", status)
        return resp.get("id")

    def login(self, session: requests.Session, username: str, password: str, status: Status) -> str:
        resp = session.post(f"{self.url}/login", json={"username": username, "password": password})

        resp = self.c.get_json(resp, "Invalid response on login", status)
        self.c.assert_eq(type(resp), dict, "Invalid response on login", status)
        if resp.get("error", "") != "":
            self.c.cquit(status, "Error on login")
        self.c.assert_eq(type(resp.get("id")), str, "Invalid response on login", status)
        self.c.assert_eq(len(resp.get("id")), 0x20, "Invalid response on login", status)
        return resp.get("id")

    def get_user(self, session: requests.Session, uid: str, status: Status) -> User:
        resp = session.post(f"{self.url}/user", json={"uid": uid})

        resp = self.c.get_json(resp, "Invalid response on get_user", status)
        self.c.assert_eq(type(resp), dict, "Invalid response on get_user", status)
        if resp.get('error', '') != '':
            self.c.cquit(status, "Error on get_user")
        self.c.assert_eq(type(resp["username"]), str, "Invalid response on get_user", status)
        self.c.assert_eq(type(resp["uid"]), str, "Invalid response on get_user", status)
        self.c.assert_eq(type(resp["balance"]), int, "Invalid response on get_user", status)
        self.c.assert_eq(resp["uid"], uid, "Invalid response on get_user", status)

        return User(username=resp["username"], uid=resp["uid"], balance=resp["balance"])

    def get_stations(self, session: requests.Session, uid: str, status: Status) -> list[Station]:
        resp = session.post(f"{self.url}/stations", json={"uid": uid})

        resp = self.c.get_json(resp, "Invalid response on get_stations", status)
        self.c.assert_eq(type(resp), list, "Invalid response on get_stations", status)
        stations: list[Station] = []
        for station in resp:
            self.c.assert_eq(type(station), dict, "Invalid response on get_stations", status)
            self.c.assert_eq(type(station["id"]), int, "Invalid response on get_stations", status)
            self.c.assert_eq(type(station["x"]), int, "Invalid response on get_stations", status)
            self.c.assert_eq(type(station["y"]), int, "Invalid response on get_stations", status)
            stations.append(Station(id=station["id"], x=station["x"], y=station["y"]))
        
        return stations

    def get_links(self, session: requests.Session, uid: str, status: Status) -> list[Link]:
        resp = session.post(f"{self.url}/links", json={"uid": uid})

        resp = self.c.get_json(resp, "Invalid response on get_links", status)
        self.c.assert_eq(type(resp), list, "Invalid response on get_links", status)
        links: list[Link] = []
        for station in resp:
            self.c.assert_eq(type(station), dict, "Invalid response on get_links", status)
            self.c.assert_eq(type(station["id1"]), int, "Invalid response on get_links", status)
            self.c.assert_eq(type(station["id2"]), int, "Invalid response on get_links", status)
            links.append(Link(id1=station["id1"], id2=station["id2"]))
        
        return links

    def get_route(self, session: requests.Session, uid: str, fr: int, to: int, status: Status) -> list[int]:
        resp = session.post(f"{self.url}/route", json={"uid": uid, "from": fr, "to": to})
        resp = self.c.get_json(resp, "Invalid response on get_route", status)
        self.c.assert_eq(type(resp), list, "Invalid response on get_route", status)

        for station_id in resp:
            self.c.assert_eq(type(station_id), int, "Invalid response on get_route", status)
        
        return resp

    def get_websocket_json(self, ws: websocket.WebSocket) -> dict:
        try:
            resp = ws.recv()
            resp = json.loads(resp)
            self.c.assert_eq(type(resp), dict, "Invalid response on websocket init", Status.MUMBLE)
            return resp
        except (UnicodeDecodeError, json.decoder.JSONDecodeError, ValueError):
            self.c.cquit(Status.MUMBLE, f"Invalid json on websocket init")

    def init_websocket(self, ws: websocket.WebSocket, uid: str) -> None:
        ws.send(json.dumps({"type":"INIT", "uid":uid}))
        resp = self.get_websocket_json(ws)
        if resp.get("data") != "ok":
            self.c.cquit(Status.MUMBLE, "Invalid response on websocket init")

    def send_oil(self, session: requests.Session, uid: str, receiver_id: str, msg: str, money: int, fr: int, to: int, status: Status) -> None:
        resp = session.post(f"{self.url}/send", json={"uid": uid, "receiver_id": receiver_id, "msg": msg, "money": money, "from": fr, "to": to})
        resp = self.c.get_json(resp, "Invalid response on send_oil", status)
        self.c.assert_eq(type(resp), dict, "Invalid response on send_oil", status)
        self.c.assert_eq(resp.get("data"), "ok", "Invalid response on send_oil", status)

    def add_money(self, session: requests.Session, uid: str, amount: int, station_id: int, oil_id: int, status: Status) -> None:
        resp = session.post(f"{self.url}/add_money", json={"uid": uid, "amount": amount, "station_id": station_id, "oil_id": oil_id})
        resp = self.c.get_json(resp, "Invalid response on add_money", status)
        self.c.assert_eq(type(resp), dict, "Invalid response on add_money", status)
        self.c.assert_eq(resp.get("data"), "ok", "Invalid response on add_money", status)

    def get_last_received_oil(self, session: requests.Session, uid: str, status: Status) -> list[Oil]:
        resp = session.post(f"{self.url}/last_received", json={"uid": uid})
        resp = self.c.get_json(resp, f"Invalid response on get_last_received_oil", status)
        self.c.assert_eq(type(resp), list, f"Invalid response on get_last_received_oil", status)

        received = []
        for oil in resp:
            self.c.assert_eq(type(oil.get("sender")), str, "Invalid response on get_last_received_oil", status)
            self.c.assert_eq(type(oil.get("message")), str, "Invalid response on get_last_received_oil", status)
            self.c.assert_eq(type(oil.get("station_id")), int, "Invalid response on get_last_received_oil", status)
            received.append(Oil(sender=oil.get("sender"), message=oil.get("message"), station_id=oil.get("station_id")))
        
        return received
