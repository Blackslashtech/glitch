from app import app
from flask import jsonify, request
import common
import json


@app.get('/api/places/public')
def get_points_of_interest():
    conn = None

    try:
        conn = common.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT addr_id, addr_label FROM places WHERE public = TRUE")
        places = cur.fetchall()

        resp = jsonify({
            "status": "ok",
            "places": [{
                "id": record[0],
                "label": record[1],
            } for record in places],
        })
    
    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e),
        }), 500
    
    finally:
        if conn is not None:
            conn.close()
    
    return resp


@app.get('/api/places/stations')
def get_stations():
    conn = None

    try:
        conn = common.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT addr_id, addr_label FROM places WHERE station = TRUE")
        places = cur.fetchall()

        resp = jsonify({
            "status": "ok",
            "stations": [{
                "id": record[0],
                "label": record[1],
            } for record in places],
        })
    
    except Exception as e:
        resp = jsonify({
            "status": "error",
            "message": str(e),
        }), 500
    
    finally:
        if conn is not None:
            conn.close()
    
    return resp
