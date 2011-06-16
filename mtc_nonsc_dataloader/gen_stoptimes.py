#!/usr/bin/env python

import csv

from math import *

def haversine(lon1, lat1, lon2, lat2):
    """
    >>> abs(haversine(-77.037852, 38.898556, -77.043934, 38.897147) - 0.549) < 0.001
    True

    """
    # convert to radians 
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 
    km = 6367 * c
    return km

VELOCITY = 6.66 # 6.66 m/s | 24 kmph

def calculate_travel_time(prev, cur):
    if prev == None or cur == None:
        raise Exception("None values are not accepted in calculations. prev = %s, cur = %s" %(prev, cur))
    distance = haversine(prev[1], prev[0], cur[1], cur[0]) * 1000
    travel_time = distance / VELOCITY
    return int(travel_time)

stop_times = []
location = {}
with open('stops.csv', 'r') as f:
    reader = csv.DictReader(f, ['stop_name', 'stop_lat', 'stop_lon'])
    for row in reader:
        if row["stop_name"] in location:
            print "Duplicate stop name %s" % row["stop_name"]
            continue
        if row["stop_lat"] == '' or row["stop_lon"] == '':
            continue
        location[row["stop_name"]] = (float(row["stop_lat"]), float(row["stop_lon"]))

routestops = []
with open('routestops.csv', 'r') as f:
    reader = csv.DictReader(f, ['route_name', 'stop_name', 'sequence'])
    for row in reader:
        routestops.append(row)

routestops_up = sorted(routestops, key=lambda row: (row['route_name'], int(row['sequence'])))
routestops_down = reversed(routestops_up)

def gen_stoptimes(routestops, trip_suffix):
    cur_route = None
    prev_stop = None
    previous_location = None
    skip_route = False
    for row in routestops:
        if cur_route != row["route_name"]:
            skip_route = False
        if skip_route:
            continue
        if cur_route == None or cur_route != row["route_name"]:
            cur_route = row["route_name"]
            stop_time = 0
            if row["stop_name"] not in location:
                skip_route = True
                continue
        else:
            if row["stop_name"] not in location:
                continue
            travel_time = calculate_travel_time(previous_location, location[row["stop_name"]])
            stop_time += travel_time
        stop_times.append({
            'trip_id' : row["route_name"] + trip_suffix,
            'stop_id' : row["stop_name"],
            'sequence' : row["sequence"],
            'stop_time' : stop_time
        })
        prev_stop = row["stop_name"]
        previous_location = location[row["stop_name"]]

gen_stoptimes(routestops_up, '-up')
gen_stoptimes(routestops_down, '-down')

with open('stoptimes.csv', 'w') as f:
    writer = csv.DictWriter(f, ['trip_id', 'stop_id', 'sequence', 'stop_time'])
    writer.writerows(stop_times)
