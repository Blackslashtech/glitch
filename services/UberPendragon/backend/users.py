from app import app
from flask import jsonify, request, make_response
from uuid import uuid5, NAMESPACE_OID
import common
import json
import random


class UsernameTaken(Exception):
    pass

class PlaceTaken(Exception):
    pass

class NoSuchUser(Exception):
    pass


@app.post('/api/users/register')
def register_user():
    conn = None

    try:
        data = json.loads(request.data)
        conn = common.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username=%s", (data["username"],))
        usernames = cur.fetchall()

        if len(usernames) > 0:
            raise UsernameTaken()

        addr_id = str(uuid5(NAMESPACE_OID, data['address']))

        cur.execute("SELECT addr_id FROM places WHERE addr_id=%s", (addr_id,))
        places = cur.fetchall()

        if len(places) > 0:
            raise PlaceTaken()

        cur.execute("SELECT homeX, homeY FROM homes")
        coords = random.choice(cur.fetchall())

        cur.execute("INSERT INTO places (addr_id, public, station, placeX, placeY) VALUES (%s, 'FALSE', 'FALSE', %s, %s)", (addr_id, *coords))
        
        cur.execute("INSERT INTO users (username, pubkey, addr_id) VALUES (%s, %s, %s)", (data["username"], data["pubkey"], addr_id))
        cur.execute("INSERT INTO doorbells (addr_id, doorb_label) VALUES (%s, %s)", (addr_id, data["doorbell"]))
        conn.commit()

        resp = jsonify({
            "status": "ok",
            }), 201

    except UsernameTaken:
            resp = jsonify({
                "status": "error",
                "message": "Username already taken"
                }), 409
    
    except PlaceTaken:
        resp = jsonify({
            "status": "error",
            "message": "Address is already occupied"
            }), 409

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()
    
    return resp


@app.get("/api/users/<username>/pubkey")
def get_pubkey(username):
    conn = None

    try:
        conn = common.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT pubkey FROM users where username=%s", (username,))
        pubkeys = cur.fetchall()

        if len(pubkeys) == 0:
            raise NoSuchUser()

        resp = jsonify({
            "status": "ok",
            "pubkey": pubkeys[0][0],
        })

    except NoSuchUser:
        resp = jsonify({
            "status": "error",
            "message": "username not in database",
        }), 404

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e),
        }), 500

    finally:
        if conn is not None:
            conn.close()
    
    return resp


def get_addr_id(username):
    conn = None

    try:
        conn = common.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT addr_id FROM users where username=%s", (username,))
        addr_ids = cur.fetchall()

        if len(addr_ids) == 0:
            raise NoSuchUser()
        
    except NoSuchUser:
        return {'status': 'error',
                'message': 'username not in database'}
    
    except Exception as e:
        return {'status': 'error',
                'message': str(e)}
    
    finally:
        if conn is not None:
            conn.close()
    
    return {'status': 'ok', 'addr_id': addr_ids[0][0]}