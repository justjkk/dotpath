#!/usr/bin/env python

from flask import Flask, render_template, g, request, abort, make_response

from dbhelper import connect_to_DB, find_nearest_node

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

@app.route("/route.kml")
def route_kml():
    if not "start_location" in request.args or not "finish_location" in request.args:
        return render_template('route.kml', kml_data=None)
    start_location = request.args["start_location"]
    finish_location = request.args["finish_location"]
    start_node = find_nearest_node(g.cur, start_location);
    finish_node = find_nearest_node(g.cur, finish_location);
    kml_rows = g.cur.execute(" \
        SELECT ST_AsKML(linemerge(the_geom)) FROM shortest_path(' \
            SELECT gid as id, \
                source::integer, \
                target::integer, \
                length::double precision as cost \
                FROM ways', \
            %d, %d, false, false) sp \
            join ways w on sp.edge_id = w.gid;" % (start_node, finish_node))
    kml_rows = g.cur.fetchall()
    if len(kml_rows) == 0:
        return render_template('route.kml', kml_data=None)
    kml_data = reduce(lambda x,y: x + y, ["<Placemark><styleUrl>#translucentPath</styleUrl>" + x[0] + "</Placemark>" for x in kml_rows])
    return render_template('route.kml', kml_data=kml_data)

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
