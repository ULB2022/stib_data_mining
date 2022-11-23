select 
gst.route_id,
gst.service_id as st_service_id,
gscd.service_id  as cd_service_id,
gst.trip_id as gst_trip_id,
st.trip_id as st_trip_id,
gst.trip_headsign,
gst.direction_id,
gst.block_id,
gst.shape_id,
st.arrival_time,
st.departure_time,
st.stop_id,
st.stop_sequence,
st.pickup_type,
st.drop_off_type,	
gscd."date" as cd_date,
gscd."day" as cd_day from "gtfs3Sept_stop_times" st 
left join
"gtfs3Sept_trips" gst on st.trip_id = gst.trip_id 
left join "calendar3sept" gscd on gst.service_id =gscd.service_id limit 10;



select  count(*) from calendar3sept_temp  gsst ;

delete 
from
	calendar3sept_temp c
where
	exists (
	select
		*
	from
		"gtfs3Sept_calendar_dates" g
	where
		g.service_id = c.service_id
		and to_date(g."date"::text, 'YYYYMMDD')= c."date"
			and g.exception_type = 2
);

insert into calendar3sept_temp select null,null,service_id,to_date("date"::text, 'YYYYMMDD'),null from "gtfs3Sept_calendar_dates"  where exception_type='1';
		
		
select * from calendar3sept_temp c,"gtfs3Sept_calendar_dates" g where
		g.service_id = c.service_id
		and to_date(g."date"::text, 'YYYYMMDD')= c."date"
			and g.exception_type = '2';
		
select * from "gtfs23Sept_calendar_dates" g   where g.exception_type = '2' and service_id =238891052;
		
		
		
		
select count(*) from calendar3sept_temp;  where service_id='238891052';




select service_id,
    to_date("date"::text, 'YYYYMMDD'),
    to_char(to_date("date"::text, 'YYYYMMDD'), 'Day'),
    '1'
from "gtfs3Sept_calendar_dates"
where exception_type = '1';



select * from calendar3sept;

insert into calendar3sept
select null,service_id,
    to_date("date"::text, 'YYYYMMDD'),
    to_char(to_date("date"::text, 'YYYYMMDD')::date, 'Day'),
    '1'
from "gtfs3Sept_calendar_dates"
where exception_type = '1';
			
			
select
		g.service_id,to_date(g."date"::text, 'YYYYMMDD'),g.exception_type
	from
		"gtfs23Sept_calendar_dates" g
	where
			g.exception_type = 2;
		
		
		
drop table "joinedStTC";


select arrival_time,count(*)             from "gtfs3Sept_stop_times" st 
            left join
            "gtfs3Sept_trips" gst on st.trip_id = gst.trip_id 
            left join "calendar3sept" gscd on gst.service_id =gscd.service_id where route_id = '20'
    and stop_id = '1748'
    and direction_id = '1'
    and gscd."date" = '2021-08-23' group by arrival_time having count(*)>1 ;

           
           
select * from "joinedSttC" jst limit 10;





select route_id,
    stop_id,
    cd_date,
    arrival_time,
    direction_id,
    st_service_id,
    gst_trip_id,
    cd_date,
    cd_day,
    processed_arrival_datetime,
    LAG(processed_arrival_datetime) OVER (
        ORDER BY processed_arrival_datetime
    ) as lag_time,
     EXTRACT(EPOCH FROM (processed_arrival_datetime - LAG(processed_arrival_datetime) OVER (
        ORDER BY processed_arrival_datetime
    )))/60 as time_diff
from "joinedsttcdebug_test" a
where route_id = '20'
    and stop_id = '1748'
    and direction_id = '1'
    and cd_date = '2021-08-23'
order by a.processed_arrival_datetime




select *  
from "joinedSttC" limit 10 offset 10000;
where route_id = '24'
    and stop_id = '4014'
    and direction_id = '1'
    and cd_date = '2021-08-23';
    
   
   
   
   
select count(*)
             from "gtfs3Sept_stop_times" st 
            left join
            "gtfs3Sept_trips" gst on st.trip_id = gst.trip_id 
            left join "calendar3sept" gscd on gst.service_id =gscd.service_id ;
            where route_id = '24'
    and stop_id = '4014'
    and direction_id = '1'
    and gscd."date" = '2021-08-23';	
    
   
   select 
   gst.route_id,
            gst.service_id as st_service_id,
            gscd.service_id  as cd_service_id,
            gst.trip_id as gst_trip_id,
            st.trip_id as st_trip_id,
            gst.trip_headsign,
            gst.direction_id,
            gst.block_id,
            gst.shape_id,
            st.arrival_time,
            st.departure_time,
            st.stop_id,
            st.stop_sequence,
            st.pickup_type,
            st.drop_off_type,
            gscd."date" as cd_date,
            gscd."day" as cd_day,
            gscd.exception as exception 
--            count(distinct(gst.trip_id, gscd.service_id,arrival_time,stop_id,direction_id,route_id))
             from "gtfs3Sept_stop_times" st 
            left join
            "gtfs3Sept_trips" gst on st.trip_id = gst.trip_id 
            left join "calendar3sept" gscd on gst.service_id =gscd.service_id where 
--            gst.trip_id =112411004235954071 and 
           gscd.service_id =235954071 and gscd."date"='2021-08-24' and stop_id ='1748';
           
select * from (select
	gst_trip_id,
	cd_service_id,
	processed_arrival_datetime,
	stop_id,
	direction_id,
	route_id,
	count(*)
from
	"joinedsttcdebug_test"
group by
	gst_trip_id,
	cd_service_id,
	processed_arrival_datetime,
	stop_id,
	direction_id,
	route_id having count(*)>1) a;
 
 


select * from calendar3sept where service_id =235954071;



select count(*) from "joinedsttcdebug_test";
 