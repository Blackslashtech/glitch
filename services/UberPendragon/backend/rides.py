from app import app
from flask import jsonify, request
import common
import json
import crypto

@app.post('/api/rides/book')
def book_a_dragon():
    conn = None
        
    try:
        data=json.loads(request.data)
        conn = common.get_connection()
        cur = conn.cursor()

        US = crypto.UberSigner()
        station, destination = US.verify(data['signature'])

        cur.execute("select doorb_label FROM doorbells WHERE addr_id = %s", (destination,))
        doorbell = [record[0] for record in cur.fetchall()][0]

        cur.execute("INSERT INTO rides (start_addr, end_addr) VALUES (%s, %s)", (station, destination))
        conn.commit()

        resp = jsonify({
            "status": "ok",
            "doorbell": doorbell,
        })

    except crypto.InvalidUberSignature as e:
        resp = jsonify({
            "status": "error",
            "message": str(e),
        }), 403

    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()
    
    return resp


@app.get('/api/rides')
def get_rides():
    conn = None

    try:
        conn = common.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT R.ride_id, P1.placeX, P1.placeY, P2.placeX, P2.placeY FROM places P1, places P2, rides R WHERE P1.addr_id = R.start_addr AND P2.addr_id = R.end_addr AND R.ride_creation > NOW() - INTERVAL '1 minutes' LIMIT 200")

        import random

        rides = [{
                'startX': ride[1],
                'startY': ride[2],
                'endX': ride[3],
                'endY': ride[4],
            } for ride in cur.fetchall()]
        
        random.shuffle(rides)

        resp = jsonify({
            "status": "ok",
            'rides': rides,
            })
    
    except Exception as e:
        print(str(e))
        resp = jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if conn is not None:
            conn.close()
    
    return resp
