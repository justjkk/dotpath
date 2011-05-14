drop table if exists mtc_routesegments;
drop table if exists mtc_routes;
drop table if exists mtc_stages;

create table mtc_stages
(
	id	serial primary key,
	name	varchar(255) not null unique,
	latitude	double precision,
	longitude	double precision
);

create table mtc_routes
(
	id	serial primary key,
	name	varchar(255) not null unique,
	source_name	varchar(255) not null,
	target_name	varchar(255) not null,
	source	integer references mtc_stages,
	target	integer references mtc_stages
);

create table mtc_routesegments
(
	id	serial primary key,
	route_name	varchar(255) not null,
	source_name	varchar(255) not null,
	target_name	varchar(255) not null,
	route	integer references mtc_routes,
	source	integer	references mtc_stages,
	target	integer references mtc_stages
);

-- Load data from file
\copy mtc_stages(name,latitude,longitude) from 'stages.csv' with csv
\copy mtc_routes(name,source_name,target_name) from 'routes.csv' with csv
\copy mtc_routesegments(route_name, source_name, target_name) from 'routesegments.csv' with csv

-- Mapping ids between stages, routes and routesegments
update mtc_routes set
	source = (select id from mtc_stages where name = source_name),
	target = (select id from mtc_stages where name = target_name);

update mtc_routesegments set
	route = (select id from mtc_routes where name = route_name),
	source = (select id from mtc_stages where name = source_name),
	target = (select id from mtc_stages where name = target_name);

-- Adding GIS column to mtc_stages
select AddGeometryColumn('mtc_stages', 'the_geom', 4326, 'POINT', 2);
update mtc_stages set the_geom = ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')', 4326);

-- Adding GIS column to mtc_routesegments
select AddGeometryColumn('mtc_routesegments', 'the_geom', 4326, 'LINESTRING', 2);

update mtc_routesegments mrsu set the_geom = ( select ST_MakeLine(s.the_geom, t.the_geom) from mtc_stages s join mtc_stages t on s.id = source and t.id = target);

-- Adding GIS column to mtc_routes
select AddGeometryColumn('mtc_routes', 'the_geom', 4326, 'MULTILINESTRING', 2);
update mtc_routes mr set the_geom = ( select ST_Union(mrs.the_geom) from mtc_routesegments mrs where mrs.route = mr.id);
