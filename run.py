#!/usr/bin/env python

from flask import Flask, render_template, g, request, abort, make_response, redirect, url_for

from dbhelper import connect_to_DB, find_nearest_node
from mtchelper import find_nearest_mtc_stage

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
    return redirect(url_for('mtc_route_kml', start_location = request.args["start_location"], finish_location = request.args["finish_location"]))


@app.route("/osm-dijkstra_route.kml")
def osm_dijkstra_route_kml():
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

@app.route("/mtc-dijkstra_route.kml")
def mtc_dijkstra_route_kml():
    if not "start_location" in request.args or not "finish_location" in request.args:
        return render_template('route.kml', kml_data=None)
    start_location = request.args["start_location"]
    finish_location = request.args["finish_location"]
    start_stage = find_nearest_mtc_stage(g.cur, start_location);
    finish_stage = find_nearest_mtc_stage(g.cur, finish_location);
    g.cur.execute(" \
        SELECT ST_AsKML(linemerge(the_geom)) FROM shortest_path(' \
            SELECT id::integer, \
                source::integer, \
                target::integer, \
                ST_Length(the_geom)::double precision as cost \
                FROM mtc_routesegments where the_geom is not null', \
            %d, %d, false, false) sp \
            join mtc_routesegments mrs on sp.edge_id = mrs.id;" % (start_stage, finish_stage))
    kml_rows = g.cur.fetchall()
    if len(kml_rows) == 0:
        return render_template('route.kml', kml_data=None)
    g.cur.execute(" \
        SELECT ST_ASKML(the_geom) FROM mtc_stages where id in (%s);" % ",".join([str(start_stage), str(finish_stage)]))
    kml_rows2 = g.cur.fetchall()
    kml_data = reduce(lambda x,y: x + y, ["<Placemark><styleUrl>#translucentPath</styleUrl>" + x[0] + "</Placemark>" for x in kml_rows])
    kml_data2 = reduce(lambda x,y: x + y, ["<Placemark><styleUrl>#Stage</styleUrl>" + x[0] + "</Placemark>" for x in kml_rows2])

    return render_template('route.kml', kml_data=kml_data + kml_data2)
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

@app.route("/osm-dijkstra")
def osm_dijkstra():
    return render_template('osm-dijkstra.html')

@app.route("/mtc-dijkstra")
def mtc_dijkstra():
    return render_template('mtc-dijkstra.html')

if __name__ == "__main__":
    app.run()
