#!/usr/bin/env python3
import checklib
import os
import random
import sys
import string
import client
from base64 import b64encode

MAX_NUM_USERS = 12
LEN_POINTS_OF_INTEREST = 5
LEN_STATIONS = 5

PORT = 5000
service_id = 'UberPendragon'

rng = random.Random()

data = checklib.get_data()
action = data['action']
if 'dev' in sys.argv:
    team_ip = '127.0.0.1'
    flag = 'A'*31 + '='
else:
    flag = data['flag']
    team_ip = f'10.{60+int(data["vulnboxId"])}.{data["teamId"]}.1'

def get_random_string(n = None):
    if n == None:
        n = rng.randint(20, 30)
    alph = string.ascii_letters + string.digits
    return "".join(rng.sample(alph, n))

def put_flag():
    flag_id = ''

    rng.seed(flag)
    try:
        username = None
        
        c = client.Client(base_url=f'http://{team_ip}:{PORT}/api', salt=get_random_string(8).encode())
        
        username, password, address = [get_random_string() for _ in range(3)]
        doorbell = flag

        c.register((username, password, address, doorbell))
        flag_id = username

    except Exception as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to register user', debug=f'{str(e)}\n{username = }')
    
    try:
        checklib.post_flag_id(service_id, data["teamId"], {"username": flag_id})

    except Exception as e:
        if 'dev' not in sys.argv:
            checklib.quit(checklib.Status.ERROR, 'Checker error', str(e))

def get_flag():
    rng.seed(flag)
    try:
        c = client.Client(base_url=f'http://{team_ip}:{PORT}/api', salt=get_random_string(8).encode())

        username, password, address = [get_random_string() for _ in range(3)]
        doorbell = flag
        
        rng.seed(os.urandom(8).hex())

        usernames = [username]
        passwords = [password]
        addresses = [address]
        doorbells = [doorbell]
        
        for i in range(rng.randint(0, MAX_NUM_USERS-1)):
            usernamei = get_random_string()

            if rng.randint(0, 3) == 0:
                # make the checker reuse passwords
                # sometimes (avoiding illegal fingerprinting
                # of exploits)
                passwordi = rng.choice(passwords)
            else:
                passwordi = get_random_string()
            
            addressi  = get_random_string()
            doorbelli = get_random_string()

            usernames.append(usernamei)
            passwords.append(passwordi)
            addresses.append(addressi)
            doorbells.append(doorbelli)

        # avoid ordered patterns in pubkey repetitions
        to_register = [(u,p,a,d) for u,p,a,d in zip(usernames[1:], passwords[1:], addresses[1:], doorbells[1:])]
        rng.shuffle(to_register)

        for user in to_register:
            c.register(user)

        idxs = list(range(len(usernames)))
        rng.shuffle(idxs)

        usernames = [usernames[i] for i in idxs]
        passwords = [passwords[i] for i in idxs]
        addresses = [addresses[i] for i in idxs]
        doorbells = [doorbells[i] for i in idxs]

        station = rng.choice(c.get_stations())['label']
        _doorbell = c.book_a_dragon(station, f'{username}\'s home', usernames, passwords)
        if doorbell != _doorbell:
            checklib.quit(checklib.Status.DOWN, comment='Got wrong doorbell', debug=f'Got {_doorbell} expected {doorbell}')

    except client.RegistrationFailed as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to register user', debug=f'{str(e)}\n{usernames}')
    except client.NoStationsAvailable as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to get stations', debug=f'{str(e)}')
    except client.RideRefused as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to book ride', debug=f'{str(e)}\n{station}\n{username}\n{usernames}\n{passwords}')
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to get doorbell', debug=f'{str(e)}\n{username}')

def check_points_of_interest(c: client.Client, _):
    places = c.get_points_of_interest()
    if len(places) < LEN_POINTS_OF_INTEREST:
        checklib.quit(checklib.Status.DOWN, comment='Missing public places', debug=f'{places}')
    return places

def check_stations(c: client.Client, _):
    stations = c.get_stations()
    if len(stations) < LEN_STATIONS:
        checklib.quit(checklib.Status.DOWN, comment='Missing stations', debug=f'{stations}')
    return stations

def check_pubkey(c: client.Client, firstuser):
    username, password, _, _ = firstuser
    pubkey = b64encode(c.get_public_key(username)).decode()
    real = c.derive_pubkey(password)
    if pubkey != real:
        checklib.quit(checklib.Status.DOWN, comment='Wrong pubkey', debug=f'Got {pubkey} for user {username} and password {password}, expected {real}')

def check_get_params(c: client.Client, _):
    c.get_params()

def check_public_flights_and_rides(c: client.Client, firstuser):
    username, password, address, doorbell = firstuser

    places = check_points_of_interest(c, firstuser)
    destination = rng.choice(places)['label']
    stations = check_stations(c, firstuser)
    station = rng.choice(stations)['label']

    usernames = [username]
    passwords = [password]
    addresses = [address]
    doorbells = [doorbell]
    
    for i in range(rng.randint(0, MAX_NUM_USERS-1)):

        usernamei = get_random_string()
        if rng.randint(0, 3) == 0:
            passwordi = rng.choice(passwords)
        else:
            passwordi = get_random_string()
        addressi  = get_random_string()
        doorbelli = get_random_string()

        usernames.append(usernamei)
        passwords.append(passwordi)
        addresses.append(addressi)
        doorbells.append(doorbelli)

    to_register = [(u,p,a,d) for u,p,a,d in zip(usernames[1:], passwords[1:], addresses[1:], doorbells[1:])]
    rng.shuffle(to_register)

    for user in to_register:
        c.register(user)
    
    users = to_register + [firstuser]
    rng.shuffle(users)

    usernames = [u[0] for u in users]
    passwords = [u[1] for u in users]

    c.book_a_dragon(station, destination, usernames, passwords)

def check_private_flights_and_rides(c: client.Client, firstuser):
    username, password, address, doorbell = firstuser

    stations = check_stations(c, firstuser)
    station = rng.choice(stations)['label']

    usernames = [username]
    passwords = [password]
    addresses = [address]
    doorbells = [doorbell]
    
    for i in range(rng.randint(0, MAX_NUM_USERS-1)):

        usernamei = get_random_string()
        if rng.randint(0, 3) == 0:
            passwordi = rng.choice(passwords)
        else:
            passwordi = get_random_string()
        addressi  = get_random_string()
        doorbelli = get_random_string()

        usernames.append(usernamei)
        passwords.append(passwordi)
        addresses.append(addressi)
        doorbells.append(doorbelli)

    to_register = [(u,p,a,d) for u,p,a,d in zip(usernames[1:], passwords[1:], addresses[1:], doorbells[1:])]
    rng.shuffle(to_register)

    for user in to_register:
        c.register(user)

    destination = f'{rng.choice(usernames)}\'s home'

    users = to_register + [firstuser]
    rng.shuffle(users)

    usernames = [u[0] for u in users]
    passwords = [u[1] for u in users]

    c.book_a_dragon(station, destination, usernames, passwords)

def check_sla():
    try:

        num_checks = rng.randint(1, 4)
        checks = [check_points_of_interest, check_stations, check_pubkey, check_get_params, check_public_flights_and_rides, check_private_flights_and_rides]

        for i in range(num_checks):
            c = client.Client(base_url=f'http://{team_ip}:{PORT}/api', salt=get_random_string(8).encode())
            username, password, address, doorbell = [get_random_string() for _ in range(4)]

            firstuser = (username, password, address, doorbell)
            
            c.register(firstuser)
            
            rng.choice(checks)(c, firstuser)
        
    except client.RegistrationFailed as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to register user', debug=f'{str(e)}\n{username}')
    except client.NoPublicPlaces as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to get public places', debug=f'{str(e)}')
    except client.NoPublicKey as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to get public key', debug=f'{str(e)}')
    except client.NoStationsAvailable as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to get stations', debug=f'{str(e)}')
    except client.NoPublicParams as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to get public params', debug=f'{str(e)}')
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, comment='Failed to check sla', debug=str(e))

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