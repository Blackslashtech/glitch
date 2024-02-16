from flask import Flask, render_template, request
import pymongo
import os


client = pymongo.MongoClient('mongodb://db:27017/')
db = client['range']

app = Flask(__name__, template_folder='templates', static_folder='static')



@app.route('/')
def index():
    try:
        max_tick = db.ticks.find_one(sort=[('tick', pymongo.DESCENDING)])['tick']
        min_tick = db.ticks.find_one(sort=[('tick', pymongo.ASCENDING)])['tick']
        tick = request.args.get('tick', default=max_tick, type=int)
        if tick > max_tick:
            tick = max_tick
        if tick < min_tick:
            tick = min_tick
        tickdata = db.ticks.find_one({'tick': tick})
        tickdata['min_tick'] = min_tick
        tickdata['max_tick'] = max_tick
        return render_template('scoreboard.html', data=tickdata, max_tick=max_tick)
    except Exception as e:
        # Redirect to loading page if there is no data
        return render_template('loading.html')
    
@app.route('/docs')
def documentation():
    return render_template('documentation.html', server_url=os.environ.get('SERVER_URL'), api_port=os.environ.get('API_PORT'))

@app.route('/api/tick')
def api_tick():
    try:
        current_tick = db.ticks.find_one(sort=[('tick', pymongo.DESCENDING)])['tick']
        return {'tick': current_tick}
    except Exception as e:
        return {'tick': 0}

@app.route('/api/loading')
def api_loading():
    try:
        good_checks = db.checks.count_documents({'code': 101})
        total_checks = db.checks.count_documents({})
        percent = int(good_checks / total_checks * 100)
        if percent == 100:
            if db.ticks.count_documents({}) == 0:
                percent = 95
        return {'percent': percent}
    except:
        return {'percent': 0}

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=80)
