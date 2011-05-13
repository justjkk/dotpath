import psycopg2

def connect_to_DB(connection_settings):
    connstr = "host=" + connection_settings["host"] + " "
    if connection_settings["port"] != "":
        connstr += "port=" + connection_settings["port"] + " "
    connstr += "dbname=" + connection_settings["dbname"] + " "
    connstr += "user=" + connection_settings["user"] + " "
    connstr += "password=" + connection_settings["password"]

    conn = psycopg2.connect(connstr)
    conn.set_isolation_level(0)
    return conn

#FIXME: Refactor me
def find_nearest_node(cur, lonlat):
    point = "POINT(" + lonlat.replace(',', ' ') + ")"
    cur.execute("select id from vertices_tmp where ST_DWithin(the_geom,st_geomfromtext(%s,4326),0.018) order by ST_Distance(the_geom, st_geomfromtext(%s,4326)) limit 1;", (point, point))
    row = cur.fetchone()
    if row != None:
        return int(row[0])
    return None
