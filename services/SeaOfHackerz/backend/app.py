import os
import json
import base64
import random
import hashlib
import string
from uuid import uuid4
from functools import wraps
from datetime import datetime, timedelta
from math import gcd
import psycopg2
from flask import Flask, request, jsonify, make_response, Response
import sympy
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class NoStyleSelectedException(Exception):
    pass


class NoTreasureError(Exception):
    pass


class InvalidSessionException(Exception):
    pass


class NotFoundError(Exception):
    pass


class ForbiddenError(Exception):
    pass


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_STATEMENT_TIMEOUT = os.getenv("POSTGRES_STATEMENT_TIMEOUT", "7000")
app = Flask(__name__)
CORS(app, supports_credentials=True)


def get_connection():
    return psycopg2.connect(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, options=f"-c statement_timeout={POSTGRES_STATEMENT_TIMEOUT}")


def validate_session(session):
    try:
        decoded = base64.b64decode(session)
        session_data = json.loads(decoded)
        random.seed(session_data["user_id"])
        salt = bytes([random.getrandbits(8) for _ in range(16)])
        salted_hash = hashlib.sha256(
            salt + str(session_data["user_id"]).encode()).hexdigest()
        if not salted_hash == session_data["salted_hash"]:
            raise InvalidSessionException()

    except Exception as e:
        raise InvalidSessionException from e

    return session_data


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with app.app_context():
            cookies = request.cookies
            if "session" not in cookies:
                return jsonify({
                    "status": "error",
                    "message": "This endpoint requires an authenticated session"
                }), 401

            try:
                session_data = validate_session(cookies["session"])
                kwargs["session_data"] = session_data

            except InvalidSessionException:
                return jsonify({
                    "status": "error",
                    "message": "Invalid session"
                }), 401

        return f(*args, **kwargs)

    return wrapper


def _get_user_items(user_id):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT item_id, personal_description FROM inventory WHERE user_id = %s", (user_id,))
        personal_items = {record[0]: record[1] for record in cur.fetchall()}
        cur.execute("SELECT * FROM items")

        items = {record[0]: {
            "id": record[0],
            "name": record[1],
            "personal_description": record[2],
        } for record in cur.fetchall()}

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500

    finally:
        if conn is not None:
            conn.close()

    resp_items = []

    for item_id in personal_items:
        item = {}
        item["item_id"] = item_id
        item["name"] = items[item_id]["name"]
        item["personal_description"] = personal_items[item_id]
        resp_items.append(item)

    return jsonify({
        "status": "ok",
        "items": resp_items}
    )


# attack management


def cryptographically_secure_prng(w, x, y, z):
    Y = bin(y)[2:].zfill(64)[::-1]

    while True:
        t = 0
        for i in Y:
            if i == '1':
                t += w
                while t > z:
                    t -= z
            w <<= 1
            w %= z
        w = (t + x) % z
        return w


@app.post("/api/users/<user_id>/attack/start")
@auth_required
def start_attack(user_id, session_data={}):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
        username = cur.fetchone()[0]

        if username == session_data["username"]:
            return jsonify({
                "status": "error",
                "message": "Can't attack yourself"
            }), 409

        cur.execute("SELECT user_id FROM users WHERE username = %s",
                    (session_data["username"],))
        att_id = cur.fetchone()[0]

        cur.execute(
            "SELECT password from users WHERE username = %s", (username,))
        password = cur.fetchone()[0]

        random.seed(int(str(uuid4()).replace('-', ''), 16))
        z = random.randint(1 << 63, 1 << 64)
        factors = sympy.factorint(z)
        primes = list(factors.keys())
        y = 1
        for p in primes:
            y *= p
        if 2 in primes and factors[2] > 1:
            y <<= 1
        while len(bin(y)[2:]) < 64:
            y *= random.choice(primes)
        y += 1
        while True:
            x = random.randint(z//10, z-1)
            if gcd(x, z) == 1:
                break
        w = random.randint(1 << 63, 1 << 64)
        w = cryptographically_secure_prng(w, x, y, z)

        cur.execute("INSERT INTO attacks (victim_id, attacker_id, ship_damage, attacker_damage, salt, w, x, y, z) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING attack_id",
                    (user_id, att_id, 0, 0, os.urandom(5).hex(), str(w), str(x), str(y), str(z)))
        attack_id = cur.fetchone()[0]
        cur.execute("UPDATE attacks SET ac_key = %s WHERE attack_id = %s", (hashlib.sha256(
            (password + str(attack_id)).encode("utf-8")).digest()[:16].hex(), attack_id))

        conn.commit()

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return jsonify({
        "status": "ok",
        "attack_id": attack_id,
    })


@app.get("/api/users/<user_id>/attack/<attack_id>")
@auth_required
def get_attack_data(user_id, attack_id, session_data={}):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
        username = cur.fetchone()[0]

        if username == session_data["username"]:
            return jsonify({
                "status": "error",
                "message": "Can't attack yourself"
            }), 409

        cur.execute("SELECT user_id FROM users WHERE username = %s",
                    (session_data["username"],))

        cur.execute(
            "SELECT ac_key, salt, w FROM attacks WHERE attack_id = %s", (attack_id,))
        ac_key, salt, w = cur.fetchone()
        ac_key = bytes.fromhex(ac_key)
        salt = bytes.fromhex(salt)

    except KeyError:
        return jsonify({
            "status": "error",
            "message": "Attack not found",
        }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return jsonify({
        "status": "ok",
        "anticheat": AES.new(ac_key, AES.MODE_ECB).encrypt(pad(salt + w.encode("utf-8"), 16)).hex(),
    })


@app.post("/api/users/<user_id>/attack/<attack_id>")
@auth_required
def perform_attack(user_id, attack_id, session_data={}):
    conn = None

    try:
        data = json.loads(request.data)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
        username = cur.fetchone()[0]

        if username == session_data["username"]:
            return jsonify({
                "status": "error",
                "message": "Can't attack yourself"
            }), 409

        cur.execute("SELECT user_id FROM users WHERE username = %s",
                    (session_data["username"],))

        cur.execute(
            "SELECT ship_damage, attacker_damage, salt, ac_key, w, x, y, z FROM attacks WHERE attack_id = %s", (attack_id,))
        ship_damage, attacker_damage, salt, ac_key, w, x, y, z = cur.fetchone()
        w = int(w)
        x = int(x)
        y = int(y)
        z = int(z)

        guess = int(data["guess"])

        if guess == w:
            response = {
                "status": "ok",
                "message": "Hit!",
                "number": w,
                "salt": salt,
                "key": ac_key,
            }
            ship_damage += 1
        else:
            response = {
                "status": "ok",
                "message": "Miss!",
                "number": w,
                "salt": salt,
                "key": ac_key,
            }
            attacker_damage += 1

        w = cryptographically_secure_prng(w, x, y, z)
        salt = os.urandom(5).hex()

        cur.execute("UPDATE attacks SET ship_damage = %s, attacker_damage = %s, salt = %s, w = %s WHERE attack_id = %s",
                    (ship_damage, attacker_damage, salt, w, attack_id))

        if ship_damage >= 15:
            response = _get_user_items(user_id)
            cur.execute(
                "DELETE FROM attacks WHERE attack_id = %s", (attack_id,))

        if attacker_damage >= 7:
            response = {
                "status": "ok",
                "message": "GameOver!",
                "number": w,
                "salt": salt,
                "key": ac_key,
            }
            cur.execute(
                "DELETE FROM attacks WHERE attack_id = %s", (attack_id,))

        conn.commit()

    except TypeError:
        return jsonify({
            "status": "error",
            "message": "Attack not found",
        }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return response


# items management


@app.get("/api/items")
def get_items():
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM items")
        resp = {
            "status": "ok",
            "items": [{
                "id": record[0],
                "name": record[1],
                "description": record[2],
            } for record in cur.fetchall()]
        }
        return jsonify(resp)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500

    finally:
        if conn is not None:
            conn.close()


@app.get("/api/user/items")
@auth_required
def get_user_items(session_data={}):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE username = %s",
                    (session_data["username"],))
        user_id = cur.fetchone()[0]

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return _get_user_items(user_id)


@app.post("/api/user/items")
@auth_required
def add_user_items(session_data={}):
    data = json.loads(request.data)
    conn = None

    try:
        conn = get_connection()
        username = session_data["username"]
        items = data["items"]

        if not items:
            raise ValueError("No items provided")

        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE username=%s",
                        (session_data["username"],))
            user_id = cur.fetchone()[0]

            cur.execute("SELECT item_id FROM items WHERE name = 'Treasure'")
            treasure_id = cur.fetchone()[0]

            if treasure_id not in [int(item['id']) for item in items]:
                raise NoTreasureError("Treasure not found")

            cur.execute("SELECT item_id FROM items")
            item_ids = [record[0] for record in cur.fetchall()]

            if not all(int(item["id"]) in item_ids for item in items):
                raise NotFoundError("Item not found")

            cur.execute("DELETE FROM inventory WHERE user_id = %s", (user_id,))

            args = []
            for item in items:
                args.append(r"(%s, %s, %s)")

            cur.execute(
                f"INSERT INTO inventory VALUES {','.join(args)}",
                tuple(sum([(user_id, int(item["id"]), item["personal_description"]) for item in items], ())))

        conn.commit()
        resp = make_response({"status": "ok"})
        resp.headers["Content-Location"] = f"/users/{username}/items"
        resp.status_code = 201

    except IndexError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except ForbiddenError:
        resp = jsonify({
            "status": "error",
            "message": "Forbidden"
        }), 403

    except NotFoundError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 404

    except ValueError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 409

    except NoTreasureError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 404

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return resp


@app.get("/api/users")
@auth_required
def get_all_users(session_data={}):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        index = int(request.args.get("page", "0"), 10)
        cur.execute("SELECT user_id, username FROM users WHERE user_id BETWEEN %s AND %s", (str(
            min_id := index*50), str(min_id+50-1)))
        if (result := cur.fetchall()) is not None:
            resp = jsonify({
                "status": "ok",
                "page": str(index),
                "users": [
                    {
                        "id": record[0],
                        "username": record[1]
                    } for record in result
                ]
            })
        else:
            resp = jsonify({
                "status": "error",
                "message": "Query failure"
            }), 500

    except ValueError:
        resp = jsonify({
            "status": "error",
            "message": "Invalid page number"
        }), 422

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return resp


@app.get("/api/users/search/<username>")
@auth_required
def search_user(username, session_data={}):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username FROM users WHERE username = %s", (username,))
        record = cur.fetchone()

        resp = jsonify({
            "status": "ok",
            "user": {
                "id": record[0],
                "username": record[1]
            }
        })

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return resp


# ships management


@app.get("/api/styles")
def get_styles():
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM styles")
        resp = jsonify({
            "status": "ok",
            "styles": [{
                "id": record[0],
                "type": record[1],
                "name": record[2],
            } for record in cur.fetchall()]
        })
    finally:
        if conn is not None:
            conn.close()

    return resp


@app.get("/api/users/<user_id>/ship")
@auth_required
def get_user_ship(user_id, session_data={}):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM ships INNER JOIN styles ON ships.style_id = styles.style_id AND ships.style_type = styles.type WHERE user_id = %s", (str(user_id),))
        resp = jsonify({
            "status": "ok",
            "ship": [{
                "type": record[0],
                "id": record[2],
                "name": record[5],
            } for record in cur.fetchall()]
        })

    except ForbiddenError:
        resp = jsonify({
            "status": "error",
            "message": "Forbidden"
        }), 403

    except NotFoundError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404

    except (IndexError, TypeError) as e:
        resp = jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    finally:
        if conn is not None:
            conn.close()

    return resp


@app.put("/api/user/ship")
@auth_required
def put_user_ship(session_data={}):
    conn = None
    username = session_data["username"]

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
        user_id = cur.fetchone()[0]

        data = json.loads(request.data)
        styles = data["styles"]

        if not styles:
            raise ValueError("No styles provided")

        with conn.cursor() as cur:

            cur.execute("SELECT type, style_id FROM styles")
            style_ids = [(record[0], record[1]) for record in cur.fetchall()]

            if not all(tuple(style) in style_ids for style in styles):
                raise NotFoundError(f"Style not found\n{list([tuple(style) for style in styles])}\n{style_ids}\n{list([tuple(style) in style_ids for style in styles])}")

            for style in styles:
                cur.execute("INSERT INTO ships VALUES (%s, %s, %s) ON CONFLICT (user_id, style_type) DO UPDATE SET style_id=%s",
                            (str(style[0]), user_id, str(style[1]), str(style[1])))

            conn.commit()
        resp = jsonify({
            "status": "ok"
        })

    except IndexError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except ForbiddenError:
        resp = jsonify({
            "status": "error",
            "message": "Forbidden"
        }), 403

    except NotFoundError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e),
        }), 404

    except ValueError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 401

    finally:
        if conn is not None:
            conn.close()

    return resp

# users management


@app.post("/api/register")
def register():
    conn = None

    try:
        data = json.loads(request.data)

        if not ((8 <= len(data["username"]) <= 30) and
                (16 <= len(data["password"]) <= 120) and
                all([c in string.ascii_letters + string.digits for c in data["username"]]) and
                all([c in string.ascii_letters + string.digits for c in data["password"]])):
            return jsonify({
                "status": "error",
                "message": "invalid username or password",
            }), 500

        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT username FROM users WHERE username=%s", (data["username"],))
            usernames = cur.fetchall()

            if any([u[0] == data["username"] for u in usernames]):
                resp = jsonify({
                    "status": "error",
                    "message": "Username already taken"
                }), 409
            else:
                cur.execute("INSERT INTO users (username, password) values (%s, %s) RETURNING user_id",
                            (data["username"], data["password"]))
                resp = jsonify({
                    "status": "ok",
                    "user_id": cur.fetchone()[0]
                })
                resp.headers["Content-Location"] = f"/users/{data['username']}"
                resp.status_code = 201
            conn.commit()

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return resp


@app.post("/api/login")
def login():
    conn = None

    try:
        data = json.loads(request.data)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * from users WHERE username = '%s' AND password = '%s'" %
                    (data["username"], data["password"]))
        results = cur.fetchall()
        if len(results) == 0:
            raise ValueError("Invalid username or password")

        user_id = results[0][0]
        random.seed(user_id)
        salt = bytes([random.getrandbits(8) for _ in range(16)])
        salted_hash = hashlib.sha256(salt + str(user_id).encode()).hexdigest()
        cookie = base64.b64encode(json.dumps({
            "username": data["username"],
            "user_id": user_id,
            "salted_hash": salted_hash
        }).encode()).decode()

        resp = jsonify({
            "status": "ok",
            "id": user_id,
            "user": data["username"],
            "cookie": cookie,
        })
        resp = make_response(resp)
        resp.set_cookie("session", cookie)

    except ValueError as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 401

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return resp


@app.get("/api/user/<user_id>")
def get_users(user_id):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT username from users WHERE user_id = %s", (user_id,))
        username = cur.fetchone()[0]

        resp = jsonify({
            "status": "ok",
            "user": username
        })

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()

    return resp


if __name__ == "__main__":
    app.run()
