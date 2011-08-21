def find_nearest_chennai_rail_stop(cur, lonlat):
    point = "POINT(" + lonlat.replace(',', ' ') + ")"
    cur.execute("select stop_id from chennai_rail.stops where ST_DWithin(the_geom,st_geomfromtext(%s,4326),0.036) order by ST_Distance(the_geom, st_geomfromtext(%s,4326)) limit 1", (point, point))
    row = cur.fetchone()
    if row != None:
        return row[0]
    return None
