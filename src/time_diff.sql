select route_id,
    stop_id,
    cd_date,
    arrival_time,
    direction_id,
    cd_date,
    processed_arrival_datetime,
    LAG(processed_arrival_datetime) OVER (
        ORDER BY processed_arrival_datetime
    ) as lag_time,
     processed_arrival_datetime - LAG(processed_arrival_datetime) OVER (
        ORDER BY processed_arrival_datetime
    ) as time_diff
from "joinedsttcdebug_test" a
where route_id = '20'
    and stop_id = '1748'
    and direction_id = '1'
    and cd_date = '2021-08-23'
order by a.processed_arrival_datetime
