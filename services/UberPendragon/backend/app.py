from flask import Flask, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import common

app = Flask(__name__)
CORS(app)

import users
import rides
import crypto


def clean_rides():
    conn = common.get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM rides WHERE ride_creation < NOW() - INTERVAL '20 minutes'")

    conn.commit()
    conn.close()


scheduler = BackgroundScheduler()
job = scheduler.add_job(clean_rides, 'interval', minutes=5)
scheduler.start()


if __name__ == "__main__":
    app.run(debug=True)