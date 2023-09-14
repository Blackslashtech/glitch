import os, sys
import ast
import json
import places

from fastecdsa.curve import secp256k1, brainpoolP256r1, P256
from fastecdsa.encoding.sec1 import SEC1Encoder as encoder

from cryptography.hazmat.primitives import hashes
from Crypto.Util.number import bytes_to_long, long_to_bytes
from functools import reduce, partial
from base64 import b64encode, b64decode

from flask import jsonify, request
from app import app
from users import get_pubkey, get_addr_id

class InvalidUberSignature(Exception):
    pass

class UnexpectedType(Exception):
    pass

class UberSigner:
    def __init__(self):
        curves = {curve.name: curve for curve in [secp256k1, brainpoolP256r1, P256]}
        params = get_params().json['params']
        self.curve = curves[params['curve']]
        self.G = self.curve.G
        self.o = self.curve.q
        self.max_users_per_ride = 12

    def encode_point(self, P):
        return b64encode(encoder.encode_public_key(P)).decode()

    def decode_point(self, Penc):
        try:
            decoded = encoder.decode_public_key(Penc, curve = self.curve)

        except ValueError as e:
            raise InvalidUberSignature('Public key point not on curve')
        
        except Exception as e:
            raise InvalidUberSignature(str(e))
        
        return decoded

    def _b64decode(self, x):
        return b64decode(x.encode()).decode()
    
    def encode(self, data):
        return b''.join(str(d).encode() for d in data)
    
    def encode_pubkeys(self, points):
        return b''.join(long_to_bytes(P.y) for P in points)
    
    def sha256(self, data):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        return bytes_to_long(digest.finalize())
    
    def Hagg(self, L, Xi):
        Xi = self.encode_pubkeys([Xi])
        return sum(L + Xi)

    def aggregate(self, pubkeys, L):
        ai = [self.Hagg(L, Xi) for Xi in pubkeys]
        Xagg = sum([ai_*Xi for Xi, ai_ in zip(pubkeys, ai)], self.G.IDENTITY_ELEMENT)
        return Xagg, ai

    def verify(self, payload: str, Hsig = None):
        if Hsig == None:
            Hsig = self.sha256

        try:
            users, pubkeys, msg, sigma = [self._b64decode(p) for p in payload.split(".")]
            users, pubkeys, (R, s) = [ast.literal_eval(x) for x in [users, pubkeys, sigma]]
            R = self.decode_point(b64decode(R.encode()))
            pubkeys = [b64decode(p.encode()) for p in pubkeys]

        except ValueError as e:
            raise InvalidUberSignature(str(e))
        
        if len(users) > self.max_users_per_ride:
            raise InvalidUberSignature('Dragon overloaded')
        
        if len(users) == 0:
            raise InvalidUberSignature('Booking an empty dragon? Really? In this economy?')
        
        if len(set(users)) != len(users):
            raise InvalidUberSignature('What? Dragons are real, clones are not')
        
        self.validate_pubkeys(pubkeys, users)

        splitted = msg.split(':')
        starting_point = splitted[0]
        destination = splitted[-1]
        
        r = places.get_stations().json
        if r['status'] == 'error':
            raise InvalidUberSignature(r['message'])
        
        stations = {station['label']:station['id'] for station in r['stations']}
        if starting_point not in stations:
            raise InvalidUberSignature('Unknown station')
        station_id = stations[starting_point]

        r = places.get_points_of_interest().json
        if r['status'] == 'error':
            raise InvalidUberSignature(r['message'])
        
        points_of_interest = {place['label']:place['id'] for place in r['places']}
        allowed_destinations = list(points_of_interest.keys()) + [f'{user}\'s home' for user in users]

        if destination not in allowed_destinations:
            raise InvalidUberSignature('Destination not allowed')

        else:
            if destination in points_of_interest.keys():
                destination_id = points_of_interest[destination]
            else:
                username = destination.removesuffix('\'s home')
                db_query = get_addr_id(username)
                
                if db_query['status'] == 'error':
                    raise InvalidUberSignature(db_query['message'])
                else:
                    destination_id = db_query['addr_id']
        
        pubkeys = [self.decode_point(Penc) for Penc in pubkeys]
        Xagg, ai = self.aggregate(pubkeys, self.encode_pubkeys(pubkeys))

        try:
            c = Hsig(self.encode([Xagg, R, msg]))

        except UnexpectedType as e:
            raise InvalidUberSignature(str(e))

        if s*self.G != (R + c*Xagg):
            raise InvalidUberSignature('Invalid signature')
        
        return station_id, destination_id
    
    def validate_pubkeys(self, pubkeys, users):
        if len(pubkeys) != len(users):
            raise InvalidUberSignature('Lengths of (users, pubkeys) mismatch')

        for user, pubkey in zip(users, pubkeys):
            true_pubkey = b64decode(get_pubkey(user).json['pubkey'].encode())
            if true_pubkey != pubkey:
                raise InvalidUberSignature(f'Pubkey doesn\'t match for user {user}')

@app.get('/api/crypto/public_params')
def get_params():
    resp = jsonify({
        'status': 'ok', 
        'params': {
            'curve': secp256k1.name
            }
        })
    
    return resp