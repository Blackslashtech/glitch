#!/usr/bin/env python3
#!/usr/bin/env python3
import checklib
import os
import sys
import requests
import random
import string
import time
from collections import defaultdict
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

PORT = 5000
service_id = 'SeaOfHackerz'

data = checklib.get_data()
action = data['action']
if 'dev' in sys.argv:
    team_ip = '127.0.0.1'
    flag = 'A'*31 + '='
else:
    flag = data['flag']
    team_ip = f'10.{60+int(data["vulnboxId"])}.{data["teamId"]}.1'

base_url = f'http://{team_ip}:{PORT}'

def get_random_string(n):
    alph = string.ascii_letters + string.digits
    return "".join(random.choice(alph) for _ in range(n))

def put_flag():
    flag_id = ''

    random.seed(flag)
    username = get_random_string(random.randint(20, 25))
    password = get_random_string(random.randint(20, 25))

    try:
        s = requests.Session()
        s.headers.update({'User-Agent': 'checker'})
        r = s.post(f'{base_url}/api/register', json={'username': username, 'password': password}).json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot register', r["message"])
        user_id = r["user_id"]
        flag_id = user_id
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot register', str(e))

    try:
        r = s.post(f'{base_url}/api/login', json={'username': username, 'password': password}).json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot login', r["message"])
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot login', str(e))

    try:
        styles = s.get(f'{base_url}/api/styles').json()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot get styles', str(e))

    try:
        styles_by_type = defaultdict(list)
        for style in styles["styles"]:
            styles_by_type[style['type']].append(style['id'])
        
        selected = []
        for t in styles_by_type:
            selected.append([t, random.choice(styles_by_type[t])])
        
        r = s.put(f'{base_url}/api/user/ship', json={'styles': selected}).json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot set styles', r["message"])
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot set styles', str(e))
    
    try:
        items = s.get(f'{base_url}/api/items').json()['items']
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot get items', str(e))

    try:
        chosen_ids = []
        selected = []
        items_without_treasure = []
        for item in items:
            if item['name'] == 'Treasure':
                selected.append({'id': item['id'], 'personal_description': flag})
                chosen_ids.append(item['id'])
            else:
                items_without_treasure.append(item)
        for i in range(random.randint(3,10)):
            while True:
                item = random.choice(items_without_treasure)
                if item['id'] not in chosen_ids:
                    break
            chosen_ids.append(item['id'])
            selected.append({'id': item['id'], 'personal_description': get_random_string(random.randint(20, 25))})

        r = s.post(f'{base_url}/api/user/items', json={'items': selected}).json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot set items', r["message"])
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot set items', str(e))
    
    try:
        checklib.post_flag_id(service_id, data["teamId"], {"userId": flag_id})
    except Exception as e:
        if 'dev' not in sys.argv:
            checklib.quit(checklib.Status.ERROR, 'Checker error', str(e))

def get_flag():
    random.seed(flag)
    username = get_random_string(random.randint(20, 25))
    password = get_random_string(random.randint(20, 25))
    
    try:
        s = requests.Session()
        s.headers.update({'User-Agent': 'checker'})
        r = s.post(f'{base_url}/api/login', json={'username': username, 'password': password}).json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot login', r["message"])
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot login', str(e))

    try:
        items = s.get(f'{base_url}/api/user/items').json()['items']
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot get personal items', str(e))

    for item in items:
        if item['name'] == 'Treasure':
            if item['personal_description'] == flag:
                # If OK
                checklib.quit(checklib.Status.OK, 'OK')
            else:
                checklib.quit(checklib.Status.DOWN, 'Cannot retrieve flag', f'Treasure exists, but {item["personal_description"]} inside')
    
    checklib.quit(checklib.Status.DOWN, 'Cannot retrieve flag', 'No treasure found')

def check_user_exists(user_id, username):
    try:
        headers = requests.utils.default_headers()
        headers.update({'User-Agent': 'checker'})
        if username != requests.get(f'{base_url}/api/user/{user_id}', headers=headers).json()['user']:
            checklib.quit(checklib.Status.DOWN, 'Cannot retrieve user', 'username not in users')
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot retrieve user', str(e))

def login(sess, username, password):
    try:
        r = sess.post(f'{base_url}/api/login', json={'username': username, 'password': password}).json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot login', r["message"])
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot login', str(e))

def set_ship(sess, username, password):
    try:
        styles = sess.get(f'{base_url}/api/styles').json()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot get styles', str(e))

    try:
        styles_by_type = defaultdict(list)
        for style in styles["styles"]:
            styles_by_type[style['type']].append(style['id'])
        
        selected = []
        for t in styles_by_type:
            selected.append([t, random.choice(styles_by_type[t])])
        
        r = sess.put(f'{base_url}/api/user/ship', json={'styles': selected})
        r = r.json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot set styles', r["message"])
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot set styles', str(e))

    return selected

def get_ship(sess, user_id, username, password, selected):
    try:
        ship = sess.get(f'{base_url}/api/users/{user_id}/ship').json()['ship']
        ids = [s["id"] for s in ship]
        if set([s[1] for s in selected]) != set(ids):
            checklib.quit(checklib.Status.DOWN, 'Got wrong ship style', f"ship style mismatch: expected{selected}, got {ids}")
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot get ship', str(e))

def set_items(sess, username, password):
    try:
        items = sess.get(f'{base_url}/api/items').json()['items']
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot get items', str(e))

    try:
        chosen_ids = []
        selected = []
        items_without_treasure = []
        for item in items:
            if item['name'] == 'Treasure':
                selected.append({'id': item['id'], 'personal_description': get_random_string(random.randint(20, 25))})
                chosen_ids.append(item['id'])
            else:
                items_without_treasure.append(item)
        for i in range(random.randint(3,10)):
            while True:
                item = random.choice(items_without_treasure)
                if item['id'] not in chosen_ids:
                    break
            chosen_ids.append(item['id'])
            selected.append({'id': item['id'], 'personal_description': get_random_string(random.randint(20, 25))})

        r = sess.post(f'{base_url}/api/user/items', json={'items': selected})
        r = r.json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot set items', r["message"])
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot set items', str(e))
    
    return selected

def get_items(sess, username, password, selected):
    try:
        items = sess.get(f'{base_url}/api/user/items').json()['items']
        items = [{'id': item['item_id'], 'personal_description': item['personal_description']} for item in items]
        if not all([s in items for s in selected]):
            checklib.quit(checklib.Status.DOWN, 'Got wrong personal items', f'personal items mismatch: expected{selected}, got {items}')
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot get personal items', str(e))

def attack(sess, target_id, target_username, target_password, selected):
    try:
        r = sess.post(f'{base_url}/api/users/{target_id}/attack/start').json()
        if r['status'] != 'ok':
            checklib.quit(checklib.Status.DOWN, 'Cannot attack', f'start attack: {r}')
        attack_id = r['attack_id']
        
        ship_damage = 0
        attacker_damage = 0

        key = hashlib.sha256((target_password + str(attack_id)).encode("utf-8")).digest()[:16]
        
        for i in range(random.randint(1, 21)):
            r = sess.get(f'{base_url}/api/users/{target_id}/attack/{attack_id}').json()
            if r['status'] != 'ok':
                checklib.quit(checklib.Status.DOWN, 'Cannot attack', f'get attack: {r}')

            anticheat = r['anticheat']

            value = unpad(AES.new(key, AES.MODE_ECB).decrypt(bytes.fromhex(anticheat)), 16)

            choice = random.randint(0, 1)
            
            if choice == 0:
                r = sess.post(f'{base_url}/api/users/{target_id}/attack/{attack_id}', json={"guess": value[5:].decode()}).json()
            else:
                r = sess.post(f'{base_url}/api/users/{target_id}/attack/{attack_id}', json={"guess": random.randint(0, 1<<64)}).json()
            if r['status'] != 'ok':
                checklib.quit(checklib.Status.DOWN, 'Cannot attack', f'post attack: {r}\n{choice = }')

            if choice == 0:
                ship_damage += 1
                if ship_damage >= 15:
                    r_items = [{'id': i['item_id'], 'personal_description': i['personal_description']} for i in r['items']]
                    if not all([s in r_items for s in selected]):
                        checklib.quit(checklib.Status.DOWN, 'Cannot attack', f'ship damage - items: got {r_items}, expected {selected}')
                    break
                elif r['message'] != "Hit!":
                    checklib.quit(checklib.Status.DOWN, 'Cannot attack', f'message "hit" not found\n{r = }\nguess: {value[5:].decode()}')
            else:
                attacker_damage += 1
                if attacker_damage < 7:
                    if r['number'] != int(value[5:].decode()):
                        checklib.quit(checklib.Status.DOWN, 'Cannot attack', f'wrong guess, wrong number: got {r["number"]}, expected {int(value[5:].decode())}\n{r = }\n{anticheat = }\n{target_password = }\n{attack_id = }')
                    elif r['salt'] != value[:5].hex():
                            checklib.quit(checklib.Status.DOWN, 'Cannot attack', f'wrong guess, wrong salt: got {r["salt"]}, expected {value[:5].hex()}\n{r = }\n{anticheat = }\n{target_password = }\n{attack_id = }')
                else:
                    break
                    
        
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot attack', str(e))


def check_sla():

    username = get_random_string(random.randint(20, 25))
    password = get_random_string(random.randint(20, 25))

    try:
        headers = requests.utils.default_headers()
        headers.update({'User-Agent': 'checker'})
        r = requests.post(f'{base_url}/api/register', headers=headers, json={'username': username, 'password': password}).json()
        if r["status"] != "ok":
            checklib.quit(checklib.Status.DOWN, 'Cannot register', r["message"])
        user_id = r["user_id"]
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, 'Cannot register', str(e))
    
    if random.randint(0, 1) == 0:
        check_user_exists(user_id, username)

    if random.randint(0, 1) == 0:
        sess1 = requests.Session()
        sess1.headers.update({'User-Agent': 'checker'})
        login(sess1, username, password)
        selected = set_ship(sess1, username, password)

        time.sleep(random.random()*3)
        sess2 = requests.Session()
        sess2.headers.update({'User-Agent': 'checker'})
        login(sess2, username, password)
        get_ship(sess2, user_id, username, password, selected)

    sess3 = requests.Session()
    sess3.headers.update({'User-Agent': 'checker'})
    login(sess3, username, password)
    selected = set_items(sess3, username, password)

    if random.randint(0, 1) == 0:
        time.sleep(random.random()*3)
        sess4 = requests.Session()
        sess4.headers.update({'User-Agent': 'checker'})
        login(sess4, username, password)
        get_items(sess4, username, password, selected)

    if random.randint(0, 1) == 0:
        username2 = get_random_string(random.randint(20, 25))
        password2 = get_random_string(random.randint(20, 25))

        try:
            headers = requests.utils.default_headers()
            headers.update({'User-Agent': 'checker'})
            r = requests.post(f'{base_url}/api/register', headers=headers, json={'username': username2, 'password': password2}).json()
            if r["status"] != "ok":
                checklib.quit(checklib.Status.DOWN, 'Cannot register', r["message"])
            user_id2 = r["user_id"]
        except Exception as e:
            checklib.quit(checklib.Status.DOWN, 'Cannot register', str(e))
        
        sess5 = requests.Session()
        sess5.headers.update({'User-Agent': 'checker'})
        login(sess5, username2, password2)
        attack(sess5, user_id, username, password, selected)

if __name__ == "__main__":
    try:
        if action == checklib.Action.CHECK_SLA.name:
            check_sla()
        elif action == checklib.Action.PUT_FLAG.name:
            put_flag()
        elif action == checklib.Action.GET_FLAG.name:
            get_flag()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, comment="Service raised an exception", debug=e)

    checklib.quit(checklib.Status.OK, 'OK')
