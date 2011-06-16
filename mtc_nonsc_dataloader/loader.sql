drop schema MTC_NonSc cascade;

create schema MTC_NonSc;

create table MTC_NonSc.Stops
(
	stop_id     text primary key,
	stop_name   text,
	stop_lat    wgs84_lat not null,
	stop_lon    wgs84_lon not null
);

create table MTC_NonSc.Trips
(
    trip_id     text primary key,
    route_id    text not null
);

create table MTC_NonSc.Stop_Times
(
	trip_id         text not null references MTC_NonSc.Trips,
	stop_id         text not null references MTC_NonSc.Stops,
	arrival_time    gtfstime not null,
    departure_time  gtfstime not null,
    stop_sequence   integer not null
);

create table MTC_NonSc.Frequencies
(
    trip_id         text not null,
    start_time      gtfstime not null,
    end_time        gtfstime not null,
    headway_secs    integer not null
);

create temporary table StopTimes
(
    trip_id        text not null,
    stop_id        text not null,
    sequence       integer not null,
    stop_time      integer not null
);

-- Load data from file
\copy MTC_NonSc.Stops(stop_id, stop_lat, stop_lon) from 'stops.csv' with csv
\copy StopTimes(trip_id, stop_id, sequence, stop_time) from 'stoptimes.csv' with csv

update MTC_NonSc.Stops set stop_name = stop_id;

-- Adding Trips from StopTimes
insert into MTC_NonSc.Trips(trip_id, route_id)
select distinct trip_id, split_part(trip_id,'-',1) from StopTimes;

\copy MTC_NonSc.Frequencies(trip_id, start_time, end_time, headway_secs) from 'frequencies.csv' with csv header

delete from MTC_Nonsc.Frequencies where trip_id not in (select trip_id from MTC_Nonsc.Trips);

-- Adding Stop_Times from StopTimes
insert into MTC_NonSc.Stop_Times(trip_id, stop_id, arrival_time, departure_time, stop_sequence)
select trip_id, stop_id, secs_to_gtfstime(stop_time), secs_to_gtfstime(stop_time), sequence from StopTimes;

-- Adding GIS column to Stops
select AddGeometryColumn('mtc_nonsc', 'stops', 'the_geom', 4326, 'POINT', 2);

update MTC_NonSc.Stops set the_geom = ST_GeomFromText('POINT(' || stop_lon || ' ' || stop_lat || ')', 4326);

