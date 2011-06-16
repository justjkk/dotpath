#!/usr/bin/env python

from flask import Flask, render_template, g, request, abort, make_response, redirect, url_for
from xml.sax.saxutils import escape

from dbhelper import connect_to_DB, find_nearest_node
from mtchelper import find_nearest_mtc_stage
from mtc_nonsc_helper import find_nearest_mtc_nonsc_stop

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
    kml_data = reduce(lambda x,y: x + y, ["<Placemark>\n<label> </label>" + x[0] + "\n</Placemark>\n" for x in kml_rows])
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
        SELECT r.name, ST_Length(rs.the_geom) as cost, ST_AsKML(linemerge(rs.the_geom)), vertex_id FROM shortest_path(' \
            SELECT id::integer, \
                source::integer, \
                target::integer, \
                ST_Length(the_geom)::double precision as cost \
                FROM mtc_routesegments where the_geom is not null', \
            %d, %d, false, false) sp \
            join mtc_routesegments rs on sp.edge_id = rs.id \
            join mtc_routes r on rs.route = r.id;" % (start_stage, finish_stage))
    kml_rows = g.cur.fetchall()
    if len(kml_rows) == 0:
        return render_template('route.kml', kml_data=None)
    stop_ids = [str(x[3]) for x in kml_rows] + [str(finish_stage)]
    g.cur.execute(" \
        SELECT name, ST_ASKML(the_geom) FROM mtc_stages where id in (%s);" % ",".join(stop_ids))
    kml_rows2 = g.cur.fetchall()
    kml_data = reduce(lambda x,y: x + y, ["<Placemark>\n<label>" + escape(x[0]) + "</label>\n" + x[2] + "\n</Placemark>\n" for x in kml_rows])
    kml_data2 = reduce(lambda x,y: x + y, ["<Placemark>\n<label>" + escape(x[0]) + "</label>\n" + x[1] + "\n</Placemark>\n" for x in kml_rows2])

    return render_template('route.kml', kml_data=kml_data + kml_data2)

@app.route("/mtc-nonsc_route.kml")
def mtc_nonsc_route_kml():
    if not "start_location" in request.args or not "finish_location" in request.args:
        return render_template('route.kml', kml_data=None)
    start_location = request.args["start_location"]
    finish_location = request.args["finish_location"]
    start_stage = find_nearest_mtc_nonsc_stop(g.cur, start_location)
    finish_stage = find_nearest_mtc_nonsc_stop(g.cur, finish_location)
    g.cur.execute(" \
        SELECT changeover_id FROM non_scheduled_route( \
            '%s', '%s', '%s')" % ('MTC_NonSc', start_stage, finish_stage))
    changeovers = [str(x[0]) for x in g.cur.fetchall()]
    if len(changeovers) == 0:
        return render_template('route.kml', kml_data=None)
    kml_rows = []
    prev = changeovers[0]
    for next_ in changeovers[1:]:
        g.cur.execute("""
            SELECT
                t.route_id,
                ST_ASKML(ST_Makeline(s.the_geom))
            FROM
                MTC_NonSc.Trips t,
                MTC_NonSc.Stops s,
                MTC_NonSc.Stop_Times st
            WHERE
                st.stop_id = s.stop_id AND
                t.trip_id = st.trip_id AND
                st.trip_id = (
                    SELECT
                        tt.trip_id
                    FROM
                        MTC_NonSc.Trips tt,
                        MTC_NonSc.Frequencies f,
                        MTC_NonSc.Stop_Times prev_st,
                        MTC_NonSc.Stop_Times next_st
                    WHERE
                        tt.trip_id = f.trip_id AND
                        prev_st.trip_id = tt.trip_id AND
                        next_st.trip_id = tt.trip_id AND
                        prev_st.stop_id = '%s' AND
                        next_st.stop_id = '%s'

                    ORDER BY f.headway_secs
                    LIMIT 1
                )
            GROUP BY t.route_id
            """ % (prev, next_)
        )
        row = g.cur.fetchone()
        kml_rows.append(row)
        prev = next_
    kml_data = reduce(lambda x,y: x + y, ["<Placemark>\n<label>" + escape(x[0]) + "</label>\n" + x[1] + "\n</Placemark>\n" for x in kml_rows])
    g.cur.execute(" \
        SELECT stop_name, ST_ASKML(the_geom) FROM MTC_NonSc.Stops where stop_id in (%s);" % ','.join(["'" + x + "'" for x in changeovers]))
    kml_rows2 = g.cur.fetchall()
    kml_data2 = reduce(lambda x,y: x + y, ["<Placemark>\n<label>" + escape(x[0]) + "</label>\n" + x[1] + "\n</Placemark>\n" for x in kml_rows2])

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

@app.route("/mtc-nonsc")
def mtc_nonsc():
    return render_template('mtc-nonsc.html')

if __name__ == "__main__":
    app.run()
