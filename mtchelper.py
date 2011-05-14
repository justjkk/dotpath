def find_nearest_mtc_stage(cur, lonlat):
    point = "POINT(" + lonlat.replace(',', ' ') + ")"
    cur.execute("select id from mtc_stages where ST_DWithin(the_geom,st_geomfromtext(%s,4326),0.036) order by ST_Distance(the_geom, st_geomfromtext(%s,4326)) limit 1;", (point, point))
    row = cur.fetchone()
    if row != None:
        return int(row[0])
    return None
