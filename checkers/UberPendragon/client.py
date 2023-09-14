import requests
import random

from fastecdsa.curve import secp256k1, brainpoolP256r1, P256
from fastecdsa.encoding.sec1 import SEC1Encoder as encoder

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Crypto.Util.number import bytes_to_long, long_to_bytes
from base64 import b64encode, b64decode
from math import ceil
from getpass import getpass
from functools import partial

class RegistrationFailed(Exception):
    pass
    
class SignatureFailed(Exception):
    pass

class RideRefused(Exception):
    pass

class NoPublicPlaces(Exception):
    pass

class NoPublicKey(Exception):
    pass

class NoPublicParams(Exception):
    pass

class UnexpectedType(Exception):
    pass

class UnknownException(Exception):
    pass

class NoStationsAvailable(Exception):
    pass

class InvalidSelection(Exception):
    pass

class CurveNotAllowed(Exception):
    pass

class PointNotOnCurve(Exception):
    pass

class Client:
    def __init__(self, base_url='http://localhost:5000/api', salt=b'salt', verbose=False):
        headers = requests.utils.default_headers()
        headers.update({'User-Agent': 'checker'})
        self.http_get = partial(requests.get, headers=headers)
        self.http_post = partial(requests.post, headers=headers)

        self.curves = {curve.name: curve for curve in [secp256k1, brainpoolP256r1, P256]}
        self.base_url = base_url
        self.salt = salt
        self.verbose = verbose
        self.get_params()

    def encode_point(self, P):
        return b64encode(encoder.encode_public_key(P)).decode()
    
    def decode_point(self, Penc):
        try:
            decoded = encoder.decode_public_key(Penc, curve = self.curve)

        except ValueError as e:
            raise PointNotOnCurve(str(e))
        
        except Exception as e:
            raise UnknownException(str(e))
        
        return decoded
    
    def encode_pubkeys(self, points):
        return b''.join(long_to_bytes(P.y) for P in points)

    def sha256(self, data):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        return bytes_to_long(digest.finalize())

    def encode(self, data):
        return b''.join(str(d).encode() for d in data)

    def register_api(self, username='', address='', doorbell='', pubkey=''):
        r = self.http_post(f'{self.base_url}/users/register', json={'username': username, 'address': address, 'doorbell': doorbell, 'pubkey': pubkey}).json()
        return r

    def derive_pubkey(self, password):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=ceil(self.o.bit_length()/8), salt=self.salt, iterations=5000)
        x = bytes_to_long(kdf.derive(password.encode()))
        X = x*self.G
        return self.encode_point(X)

    def register(self, params=None):
        if params is None:
            username = input('\nUsername              > ')
            password = getpass(prompt='Password              > ')
            address  = input('What\'s your address?  > ')
            doorbell = input('Doorbell details?     > ')
        else:
            username, password, address, doorbell = params

        pubkey = self.derive_pubkey(password)
        r = self.register_api(username, address, doorbell, pubkey)

        if r['status'] == 'error':
            raise RegistrationFailed(r['message'])
        
        if self.verbose:
            print('\nRegistration successful!')

    def get_params(self):
        r = self.http_get(f'{self.base_url}/crypto/public_params').json()

        if ('params' not in r) or ('curve' not in r['params']):
            raise NoPublicParams()
        
        curve = r['params']['curve']
        if curve not in self.curves:
            raise CurveNotAllowed()
        
        self.curve = self.curves[curve]
        self.G = self.curve.G
        self.o = self.curve.q

    def get_public_key(self, username):
        r = self.http_get(f'{self.base_url}/users/{username}/pubkey').json()

        if r['status'] == 'error':
            raise NoPublicKey(f'{username}')
        if 'pubkey' not in r:
            raise NoPublicKey()
        
        return b64decode(r['pubkey'].encode())

    def get_points_of_interest(self):
        r = self.http_get(f'{self.base_url}/places/public').json()
        
        if r['status'] == 'error':
            raise NoPublicPlaces(r['message'])
        if ('places' not in r) or (r['places'] == []):
            raise NoPublicPlaces()

        return r['places']

    def get_passwords(self, list_users):
        for user in list_users:
            password = getpass(prompt=f'\nPlease {user} insert your password:\n> ')
            yield password
        
    def Hagg(self, L, Xi):
        Xi = self.encode_pubkeys([Xi])
        return sum(L + Xi)

    def aggregate(self, pubkeys, L):
        ai = [self.Hagg(L, Xi) for Xi in pubkeys]
        Xagg = sum([ai_*Xi for Xi, ai_ in zip(pubkeys, ai)], self.G.IDENTITY_ELEMENT)
        return Xagg, ai

    def sign(self, list_users, msg, Hsig = None, passwords = None):
        if Hsig == None:
            Hsig = self.sha256

        pubkeys = [self.decode_point(self.get_public_key(username)) for username in list_users]
        Xagg, ai = self.aggregate(pubkeys, self.encode_pubkeys(pubkeys))
        pubkeys = [self.encode_point(P) for P in pubkeys]
    
        ri = [random.randrange(self.o) for _ in list_users]
        Ri = [ri_*self.G for ri_ in ri]
        R = sum(Ri, self.G.IDENTITY_ELEMENT)
        c = Hsig(self.encode([Xagg, R, msg]))

        if passwords == None:
            passwords = self.get_passwords(list_users)

        s = 0
        for ri_, ai_, password in zip(ri, ai, passwords):
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=ceil(self.o.bit_length()/8), salt=self.salt, iterations=5000)
            xi_ = int.from_bytes(kdf.derive(password.encode()), 'big')
            s += ri_ + c*ai_*xi_
            s %= self.o
        
        return (self.encode_point(R), s), pubkeys

    def get_stations(self):
        r = self.http_get(f'{self.base_url}/places/stations').json()

        if r['status'] == 'error':
            raise NoStationsAvailable(r['message'])
        if 'stations' not in r:
            raise NoStationsAvailable()
        
        return r['stations']

    def book_a_dragon(self, station, destination, usernames, passwords = None, graphics = False):
        msg = f'{station}:{destination}'
        sigma, pubkeys = self.sign(usernames, msg, passwords = passwords)

        payload = b'.'.join([b64encode(str(x).encode()) for x in [usernames, pubkeys, msg, sigma]]).decode()

        r = self.http_post(f'{self.base_url}/rides/book', json={
            'signature': payload
            }).json()
        
        if r['status'] == 'error':
            raise RideRefused(r['message'])
        if 'doorbell' not in r:
            raise RideRefused('No doorbell retrieved')
        
        if graphics:
            from PIL import Image
            from PIL import ImageFont
            from PIL import ImageDraw
            from io import BytesIO

            img = self.http_get(f'{":".join(self.base_url.split(":")[:-1])}:80/doorbell.png').content
            
            im = Image.open(BytesIO(img)).convert('RGBA')
            w, h = im.size
            draw = ImageDraw.Draw(im)
            db = r['doorbell']
            font = ImageFont.truetype("./Cochin Regular.otf", 20)
            bbox = draw.textbbox((0,0),text=db, font=font)
            W = bbox[2] - bbox[0]
            H = bbox[3] - bbox[1]
            draw.multiline_text(((w-W)//2, (h-H-100)//2), db, fill='black', font=font, align='center')

            im.show()
        
        if self.verbose:
            print('\nHere we are! Hope you had a pleasant trip')
            
        return r['doorbell']
    
    def view_map(self):
        from PIL import Image
        from io import BytesIO

        img = self.http_get(f'{":".join(self.base_url.split(":")[:-1])}:80/clientMap.png').content
        im = Image.open(BytesIO(img)).convert('RGBA')

        im.show()
    
    def select_starting_point(self):
        possible_stations = self.get_stations()
        print('\nPlease select your starting point:')
        for idx, station in enumerate(possible_stations):
            print(f'{idx+1})', station['label'])
        ans = int(input('> ')) -1

        if not (0 <= ans < len(possible_stations)):
            raise InvalidSelection()

        return possible_stations[ans]['label']
    
    def select_destination(self, users):
        points_of_interest = self.get_points_of_interest()
        print('\nPlease select your destination:')
        for idx, place in enumerate(points_of_interest):
            print(f'{idx+1})', place['label'])
        for jdx, user in enumerate(users):
            print(f'{idx+2+jdx}) {user}\'s home')
        ans = int(input('> ')) -1

        if not (0 <= ans < len(points_of_interest) + len(users)):
            raise InvalidSelection()

        if ans < len(points_of_interest):
            return points_of_interest[ans]['label']

        return f'{users[ans-idx-1]}\'s home'

    def users_for_ride(self):
        users = input('\nPlease provide the username(s) of all the passengers for this ride, comma separated (i.e. user1,user2,user3):\n> ')
        return users.split(',')

BANNER = r'''
                                  ______________________________________________________________________________
                             ()==(                                                                              (@==()
            \||/                 '_____________________________________________________________________________'|
            |  @___oo              |        _                                    _                              |
      /\  /\ / (__,,,,|            |       | |                                  | |                             |
     ) /^\) ^\/ _)                 |  _   _| |__   ___ _ __ _ __   ___ _ __   __| |_ __ __ _  __ _  ___  _ __   |
     )   /^\/   _)                 | | | | | '_ \ / _ \ '__| '_ \ / _ \ '_ \ / _` | '__/ _` |/ _` |/ _ \| '_ \  |
     )   _ /  / _)                 | | |_| | |_) |  __/ |  | |_) |  __/ | | | (_| | | | (_| | (_| | (_) | | | | |
 /\  )/\/ ||  | )_)                |  \__,_|_.__/ \___|_|  | .__/ \___|_| |_|\__,_|_|  \__,_|\__, |\___/|_| |_| |
<  >      |(,,) )__)               |                       | |                                __/ |             |
 ||      /    \)___)\              |                       |_|                               |___/              |
 | \____(      )___) )___        __)____________________________________________________________________________|
  \______(_______;;; __;;;  ()==(                                                                               (@==()
                                 '------------------------------------------------------------------------------'
'''

def menu():
    ans = input('''\nWhat do you want to do?
1) Register
2) Book a dragon
3) View map
> ''')
    return ans

if __name__ == "__main__":
    print(BANNER)
    C = Client(verbose=True)
    while True:
        try:
            choice = menu()
            if choice == '1':
                C.register()
            elif choice == '2':
                users_to_transport = C.users_for_ride()
                starting_point = C.select_starting_point()
                destination = C.select_destination(users_to_transport)
                print(C.book_a_dragon(starting_point, destination, users_to_transport, graphics=True))
            elif choice == '3':
                C.view_map()
            else:
                continue

        except Exception as e:
            print('\nException occurred:', str(e))

