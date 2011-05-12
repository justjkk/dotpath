#!/usr/bin/env python

from flask import Flask, render_template, g, request, abort, make_response

from dbhelper import connect_to_DB

app = Flask(__name__)
app.config.from_object('configuration')

db = connect_to_DB(app.config['CONNECTION_SETTINGS'])

@app.before_request
def before_request():
    g.cur = db.cursor()

@app.after_request
def after_request(response):
    g.cur.close()
    return response

@app.route("/routing.js", methods=["GET"])
def routing_js():
    if not "start_location" in request.args or not "finish_location" in request.args:
        abort(404)
    data = request.args
    response = make_response(render_template('routing.js', data=data), 200)
    response.headers["Content-Type"] = "text/javascript; charset=utf-8"
    return response
    
@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
