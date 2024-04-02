#!/usr/bin/env python3

import math
import sys
import time
import random
import requests

from checklib import *
from neftetochka_lib import *

INITIAL_BALANCE = 500

STATIONS = frozenset([
    Station(id=16001, x= 1, y= 2),
    Station(id=16002, x= 3, y= 5),
    Station(id=16003, x=15, y= 2),
    Station(id=16005, x= 5, y=13),
    Station(id=16006, x=15, y=14),
    Station(id=16007, x= 3, y= 9),
    Station(id=16008, x= 9, y= 3),
    Station(id=16009, x=20, y= 4),
    Station(id=16011, x=11, y=20),
    Station(id=16012, x= 8, y=17),
    Station(id=16013, x= 2, y=19),
    Station(id=16014, x=10, y=11),
    Station(id=16015, x=19, y=19),
    Station(id=16016, x=13, y= 4),
    Station(id=16017, x= 6, y= 1),
    Station(id=16018, x= 0, y=12),
    Station(id=16019, x= 7, y= 8),
    Station(id=16020, x=18, y= 1),
    Station(id=16021, x= 3, y=16),
    Station(id=16022, x=13, y=16),
    Station(id=16024, x=16, y= 7),
    Station(id=16023, x=14, y= 9),
    Station(id=16010, x=19, y=10),
    Station(id=16004, x=10, y= 5),
    Station(id=16025, x=17, y=11),
    Station(id=16026, x=11, y=17),
    Station(id=16027, x=16, y=18),
    Station(id=16028, x=17, y=16),
    Station(id=16029, x= 6, y= 5),
    Station(id=16030, x= 7, y=11),
    Station(id=16031, x=14, y=12),
    Station(id=16032, x=17, y= 4),
    Station(id=16033, x=12, y=14),
    Station(id=16034, x= 9, y=15),
])

LINKS = frozenset([
    Link(id1=16001, id2=16017),
    Link(id1=16001, id2=16002),
    Link(id1=16017, id2=16008),
    Link(id1=16016, id2=16003),
    Link(id1=16002, id2=16007),
    Link(id1=16018, id2=16007),
    Link(id1=16019, id2=16004),
    Link(id1=16020, id2=16003),
    Link(id1=16020, id2=16009),
    Link(id1=16019, id2=16007),
    Link(id1=16013, id2=16021),
    Link(id1=16005, id2=16021),
    Link(id1=16005, id2=16012),
    Link(id1=16021, id2=16012),
    Link(id1=16008, id2=16004),
    Link(id1=16008, id2=16016),
    Link(id1=16011, id2=16026),
    Link(id1=16022, id2=16026),
    Link(id1=16022, id2=16006),
    Link(id1=16024, id2=16023),
    Link(id1=16015, id2=16027),
    Link(id1=16028, id2=16027),
    Link(id1=16028, id2=16006),
    Link(id1=16025, id2=16010),
    Link(id1=16025, id2=16023),
    Link(id1=16012, id2=16026),
    Link(id1=16002, id2=16029),
    Link(id1=16008, id2=16029),
    Link(id1=16014, id2=16019),
    Link(id1=16014, id2=16030),
    Link(id1=16005, id2=16030),
    Link(id1=16006, id2=16031),
    Link(id1=16025, id2=16031),
    Link(id1=16009, id2=16032),
    Link(id1=16024, id2=16032),
    Link(id1=16012, id2=16034),
    Link(id1=16033, id2=16022),
    Link(id1=16033, id2=16031),
])

STATIONS_IDS = [station.id for station in STATIONS]
STATIONS_DICT = {station.id: station for station in STATIONS}

PASSED = "passed"
NO_MONEY = "no_money"
GET = "get"

class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 10
    uses_attack_data: bool = False
    
    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

        stations: dict[int, list[int]] = {}
        for link in LINKS:
            if link.id1 not in stations:
                stations[link.id1] = []
            if link.id2 not in stations:
                stations[link.id2] = []
            stations[link.id1].append(link.id2)
            stations[link.id2].append(link.id1)
        self.stations = stations

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')
        except (ConnectionRefusedError, websocket.WebSocketBadStatusException, websocket.WebSocketProtocolException):
            self.cquit(Status.DOWN, 'Connection error', 'Got websocket connection error')
        except websocket.WebSocketTimeoutException:
            self.cquit(Status.DOWN, 'Connection error', 'Got websocket timeout error')

    def _get_fr_to(self) -> tuple[int, int]:
        fr = random.choice(STATIONS_IDS)
        to = random.choice(STATIONS_IDS)
        while fr == to:
            to = random.choice(STATIONS_IDS)
        return fr, to

    def _get_dist_sqr(self, id1: int, id2: int) -> int:
        x1, y1 = STATIONS_DICT[id1].x, STATIONS_DICT[id1].y
        x2, y2 = STATIONS_DICT[id2].x, STATIONS_DICT[id2].y
        dist_sqr = (x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)
        return dist_sqr

    def _get_route_cost(self, route: list[int]) -> int:
        cost = 0
        for i in range(len(route) - 1):
            cost += math.ceil(math.sqrt(self._get_dist_sqr(route[i+1], route[i])))
        return cost

    def _calc_route(self, fr: int, to: int) -> list[int]:
        d = {fr: 0}
        p = {}
        q = [(0, fr),]
        while len(q) > 0:
            v = min(q)[1]
            q.remove(min(q))
            for u in self.stations[v]:
                dist = self._get_dist_sqr(u, v)
                if (u not in d) or (d[u] > d[v] + dist):
                    d[u] = d[v] + dist
                    p[u] = v
                    q.append((d[u], u))
        if to not in d:
            return []
        r = []
        x = to
        while x != fr:
            r.append(x)
            x = p[x]
        r.append(x)
        return r        

    def _check_stations(self, stations: list[Station]) -> bool:
        for station in stations:
            if station not in STATIONS:
                return False
        return len(stations) == len(STATIONS)

    def _check_links(self, links: list[Link]) -> bool:
        for link in links:
            if link not in LINKS:
                return False
        return len(links) == len(LINKS)

    def _check_route(self, fr: int, to: int, route: list[int]) -> bool:
        correct_route = self._calc_route(fr, to)
        return correct_route == route

    def _calc_expected_ans(self, fr: int, to: int, money: int) -> list[dict]:
        if money < 0:
            return [{"type": NO_MONEY, "station_id": fr, "money": money}]
        route = self._calc_route(fr, to)
        res = []
        res.append({"type": PASSED if len(route) > 1 else GET, "station_id": fr, "money": money})

        for i in range(len(route)-2, -1, -1):
            dist_sqr = self._get_dist_sqr(route[i+1], route[i])
            cost = math.ceil(math.sqrt(dist_sqr))
            money -= cost
            res.append({"station_id": route[i]})
            if money < 0:
                res[-1]["type"] = NO_MONEY
                res[-1]["money"] = money
                break
            if i > 0:
                res[-1]["type"] = PASSED
                res[-1]["money"] = money
            else:
                res[-1]["type"] = GET
        return res
    
    def _send_oil(self, session: requests.Session, sender_uid: str, receiver_uid: str, msg: str, money: int, fr: int, to: int) -> None:
        expected_ans = self._calc_expected_ans(fr, to, money)[::-1]
        ws = self.mch.get_websocket()
        time.sleep(1)
        self.mch.init_websocket(ws, sender_uid)
        self.mch.send_oil(session, sender_uid, receiver_uid, msg, money, fr, to, Status.MUMBLE)
        while True:
            resp = self.mch.get_websocket_json(ws)
            ans = expected_ans.pop()
            self.assert_eq(resp.get("type"), ans["type"], "Invalid response from websocket while sending oil")
            self.assert_eq(resp.get("station_id"), ans["station_id"], "Invalid response from websocket while sending oil")
            self.assert_eq(resp.get("receiver_id"), receiver_uid, "Invalid response from websocket while sending oil")
            if ans["type"] == GET:
                ws.close()
                break
            if ans["type"] == PASSED:
                self.assert_eq(resp.get("money"), ans["money"], "Invalid response from websocket while sending oil")
                continue
            if ans["type"] == NO_MONEY:
                self.assert_eq(resp.get("money"), ans["money"], "Invalid response from websocket while sending oil")
                self.assert_eq(type(resp.get("oil_id")), int, "Invalid response from websocket while sending oil")
                amount = random.randint(1, 20)
                self.mch.add_money(session, sender_uid, amount, resp.get("station_id"), resp.get("oil_id"), Status.MUMBLE)
                money = resp.get("money") + amount
                expected_ans = self._calc_expected_ans(resp.get("station_id"), to, money)[::-1]

    def check(self):
        session = get_initialized_session()
        username, password = rnd_username(8), rnd_password()

        reg_uid = self.mch.register(session, username, password, Status.MUMBLE)
        log_uid = self.mch.login(session, username, password, Status.MUMBLE)
        assert_eq(reg_uid, log_uid, "uid on register != uid on login")

        init_user = self.mch.get_user(session, log_uid, Status.MUMBLE)
        assert_eq(init_user.uid, log_uid, "get_user returned invalid uid")
        assert_eq(init_user.username, username, "get_user returned invalid username")
        assert_eq(init_user.balance, INITIAL_BALANCE, "get_user returned invalid balance")

        stations = self.mch.get_stations(session, log_uid, Status.MUMBLE)
        assert_eq(self._check_stations(stations), True, "get_stations returned invalid stations")

        links = self.mch.get_links(session, log_uid, Status.MUMBLE)
        assert_eq(self._check_links(links), True, "get_links returned invalid links")

        fr, to = self._get_fr_to()
        route = self.mch.get_route(session, log_uid, fr, to, Status.MUMBLE)
        assert_eq(self._check_route(fr, to, route), True, "get_route returned invalid route")

        uid1 = log_uid
        uid2 = self.mch.register(session, rnd_username(8), rnd_password(), Status.MUMBLE)

        msg = rnd_string(random.randint(5, 40))
        money = random.randint(1, 20)

        self._send_oil(session, uid1, uid2, msg, money, fr, to)

        session = get_initialized_session()
        received = self.mch.get_last_received_oil(session, uid2, Status.MUMBLE)
        assert_eq(len(received), 1, "Invalid data on get_last_received_oil")

        assert_eq(received[0].message, msg, "Invalid data on get_last_received_oil")
        assert_eq(received[0].sender, username, "Invalid data on get_last_received_oil")
        assert_eq(received[0].station_id, to, "Invalid data on get_last_received_oil")

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        sender = self.mch.register(session, rnd_username(8), rnd_password(), Status.MUMBLE)
        receiver = self.mch.register(session, rnd_username(8), rnd_password(), Status.MUMBLE)

        fr, to = self._get_fr_to()
        self.mch.get_route(session, sender, fr, to, Status.CORRUPT)
        money = random.randint(1, 20)

        self._send_oil(session, sender, receiver, flag, money, fr, to)

        self.cquit(Status.OK, f'{receiver}')

    def get(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        receiver = flag_id

        received = self.mch.get_last_received_oil(session, receiver, Status.CORRUPT)

        messages = [oil.message for oil in received]

        self.assert_eq(flag in messages, True, "Received oil is invalid", Status.CORRUPT)

        self.cquit(Status.OK)


if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
