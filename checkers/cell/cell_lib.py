import requests
from checklib import *
import websockets
import json


PORT = 8008

class CheckMachine:
    @property
    def api_url(self):
        return f'http://{self.c.host}:{PORT}/api'
    
    @property
    def ws_url(self):
        return f'ws://{self.c.host}:{PORT}/connection/websocket'

    def __init__(self, checker: BaseChecker):
        self.c = checker

    def register(self, session: requests.Session, username: str, password: str):
        resp = session.post(self.api_url + '/signup', json={'login': username, 'password': password})
        self.c.check_response(resp, 'Failed to signup')
        js = self.c.get_json(resp, 'Failed to signup')
        self.c.assert_eq(type(js), dict, 'Failed to signup: invalid JSON returned')
        return js

    def login(self, session: requests.Session, username: str, password: str, status: Status = Status.MUMBLE):
        resp = session.post(self.api_url + '/signin', json={'login': username, 'password': password})
        self.c.check_response(resp, 'Failed to signin', status)
        js = self.c.get_json(resp, 'Failed to signin', status)
        self.c.assert_eq(type(js), dict, 'Failed to signin: invalid JSON returned')
        return js

    def create_sheet(self, session: requests.Session, title: str):
        resp = session.post(self.api_url + '/sheets/create', json={'title': title})
        self.c.check_response(resp, 'Failed to create sheet')
        js = self.c.get_json(resp, 'Failed to create sheet')
        self.c.assert_eq(type(js), dict, 'Failed to create sheet: invalid JSON returned')
        return js
    
    def upload_sheet(self, session: requests.Session, title: str, file_path: str):
        resp = session.post(self.api_url + '/sheets/upload', 
                            files = {
                                'sheet': 
                                (title, open(file_path, 'rb'))
                            })
        self.c.check_response(resp, 'Failed to upload sheet')
        js = self.c.get_json(resp, 'Failed to upload sheet')
        self.c.assert_eq(type(js), dict, 'Failed to upload sheet: invalid JSON returned')
        return js

    def get_sheet(self, session: requests.Session, sheet_id: str, token:str, status: Status = Status.MUMBLE):
        resp = session.get(self.api_url + f'/sheets/{sheet_id}', params={'token': token})
        self.c.check_response(resp, 'Failed to get sheet', status=status)
        js = self.c.get_json(resp, 'Failed to get sheet', status=status)
        self.c.assert_eq(type(js), dict, 'Failed to get sheet: invalid JSON returned')
        return js
    
    def user_sheets(self, session: requests.Session, status: Status = Status.MUMBLE):
        resp = session.get(self.api_url + '/sheets')
        self.c.check_response(resp, 'Failed to get user sheets', status=status)
        ls = self.c.get_json(resp, 'Failed to get user sheets', status=status)
        self.c.assert_eq(type(ls), list, 'Failed to get user sheets: invalid JSON returned', status=status)
        return ls

    def connect(self, ws: websockets.sync.connection.Connection, op_id: int):
        payload = {
            "id": op_id,
            "connect": {},
        }

        ws.send(json.dumps(payload))

        msg = self.c.decode_json(ws.recv(), 'Invalid JSON received from connect')
        self.c.assert_eq(msg.get('id'), op_id, 'Invalid id in connect response')
        return msg
    
    def subscribe(self, ws: websockets.sync.connection.Connection, op_id: int, sheet_id: str, token: str):
        payload = {
            "id": op_id,
            "subscribe": {
                "channel": f"sheets:{sheet_id}",
                "data": {"authToken": token},
                "user": "",
            }
        }

        ws.send(json.dumps(payload))

        msg = self.c.decode_json(ws.recv(), 'Invalid JSON received from Subscribe channel')
        self.c.assert_eq(msg.get('id'), op_id, 'Invalid id in Subscribe channel response')
        return msg
        
    
    def modify_cell(self, ws: websockets.sync.connection.Connection, op_id: int, sheet_id: str, cell: str, value: str, token: str, timeout: int = None):
        payload = {
            "id": op_id,
            "rpc": {
                "method": "sheets.write",
                "data": {
                    "sheetId": sheet_id,
                    "cell": cell,
                    "value": value,
                    "authToken": token,
                }
            }
        }

        ws.send(json.dumps(payload))
        msg = self.c.decode_json(ws.recv(timeout=timeout), 'Invalid JSON received from RPC')
        if not msg:
            raise TimeoutError("Got empty response")

        self.c.assert_eq(type(msg), dict, 'Invalid JSON received from RPC')
        self.c.assert_eq(msg.get('id'), op_id, 'Invalid id in RPC response')
        return msg

