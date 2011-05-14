#!/usr/bin/env python

import csv

routesegments = []
with open('routestages.csv', 'r') as f:
	reader = csv.DictReader(f, ['route_name', 'stage_name', 'sequence'])
	cur_route = None
	prev_stage = None
	for row in reader:
		if cur_route == None or cur_route != row["route_name"]:
			cur_route = row["route_name"]
			prev_stage = row["stage_name"]
			continue
		routesegments.append((cur_route, prev_stage, row["stage_name"]))
		prev_stage = row["stage_name"]

with open('routesegments.csv', 'w') as f:
	writer = csv.writer(f)
	writer.writerows(routesegments)
