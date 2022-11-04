from flask import Flask, render_template, request, make_response, jsonify
import requests
import time

STATS_URL = 'stats'

app = Flask(__name__, instance_relative_config=True)

# increment the stats for a service and operation
def update_stats(service, op):
    x = requests.post(STATS_URL + f'/{service}/{op}', timeout=10)
    x.raise_for_status()
    return x.json()


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