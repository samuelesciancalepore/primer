from flask import Flask, render_template, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import time

stats_db = "stats_db"
user = "stats"
password = "stats"

app = Flask(__name__, instance_relative_config=True)


app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{user}:{password}@{stats_db}/{stats_db}"

db = SQLAlchemy(app)

class Stats(db.Model):
    service = db.Column(db.String(100), primary_key = True)
    op = db.Column(db.String(100), primary_key = True)
    visits = db.Column(db.Integer)

    def __init__(self, service, op, visits = 0):
        self.service = service
        self.op = op
        self.visits = visits

with app.app_context():
    # retry, it is very slow to init the mysql db
    for i in range(100):
        try:
            db.create_all()
            print("created tables")
            break
        except:
            time.sleep(5)

# increment the stats for a service and operation
def update_stats(service, op):
    with app.app_context():
        stat = db.session.query(Stats).filter_by(service=service, op=op).first()
        if stat is None:
            stat = Stats(service, op)
        stat.visits += 1
        db.session.add(stat)
        db.session.commit()

@app.route('/add')
def add():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    if a and b:
        update_stats('math','add')
        return make_response(jsonify(s=a+b), 200)
    else:
        return make_response('Invalid input\n', 400)

@app.route('/sub')
def sub():
    a = request.args.get('a', 0, type=float)
    b = request.args.get('b', 0, type=float)
    update_stats('math', 'sub')
    return make_response(jsonify(s=a-b), 200)

@app.route('/mul')
def mul():
    a = request.args.get('a', 0, type=float)
    b = request.args.get('b', 0, type=float)
    update_stats('math', 'mul')
    return make_response(jsonify(s=a*b), 200)

@app.route('/div')
def div():
    a = request.args.get('a', 0, type=float)
    b = request.args.get('b', 0, type=float)
    if b == 0:
        return make_response('Cannot divide by zero\n', 400)
    else:
        update_stats('math', 'div')
        return make_response(jsonify(s=a/b), 200)

@app.route('/mod')
def mod():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    if b == 0:
        return make_response('Cannot mod by zero\n', 400)
    else:
        update_stats('math', 'mod')
        return make_response(jsonify(s=a%b), 200)

def create_app():
    return app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)