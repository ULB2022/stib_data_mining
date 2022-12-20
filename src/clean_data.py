from sqlalchemy import create_engine
from initial_setup import *
dateid='2021-9-11'
route_id=6
direction_id=1

dates = ['2021-09-06', '2021-09-07', '2021-09-08', '2021-09-09', '2021-09-10', '2021-09-11', '2021-09-12', '2021-09-13','2021-09-14',
'2021-09-15','2021-09-16','2021-09-17','2021-09-18','2021-09-19']
# df=pd.read_sql(f"""select *, min(processed_arrival_datetime) OVER(PARTITION BY (gst_trip_id, cd_date) ) AS start_time
# from mapped_data_latest m where route_id={route_id} and direction_id=0 and cd_date ='{dateid}' and direction_id={direction_id} order by start_time,gst_trip_id ,stop_sequence;""",engine)
df=None

threshold = 6
df_cleaned = None

def remove_anomaly(x,dateid):

    if ( pd.notnull(x['dim_lag']) and abs(x['delay_in_min'] -x['dim_lag'])>threshold) and ( pd.notnull(x['dim_lead']) and abs(x['delay_in_min'] -x['dim_lead'])>threshold):

        # logger.info(f'Cleaned Trip id {trip_id} for date {dateid} - arrival time {x["processed_arrival_time"]}')
        # file_object.write(f'Cleaned Trip id {trip_id} for date {dateid} - arrival time {x["processed_arrival_time"]}')
        return (x['dim_lag']+x['dim_lead'])/2
    if ( pd.isnull(x['dim_lag'])) and ( pd.notnull(x['dim_lead']) and abs(x['delay_in_min'] -x['dim_lead'])>threshold):
        # logger.info(f'Cleaned Trip id {trip_id} for date {dateid} - arrival time {x["processed_arrival_time"]}')
        # file_object.write(f'Cleaned Trip id {trip_id} for date {dateid} - arrival time {x["processed_arrival_time"]}')
        return x['dim_lead']
    if ( pd.notnull(x['dim_lag']) and abs(x['delay_in_min'] -x['dim_lag'])>threshold) and ( pd.isnull(x['dim_lead'])):

        # logger.info(f'Cleaned Trip id {trip_id} for date {dateid} - arrival time {x["processed_arrival_time"]}')
        # file_object.write(f'Cleaned Trip id {trip_id} for date {dateid} - arrival time {x["processed_arrival_time"]}')
        return x['dim_lag']
    else:
        return x['delay_in_min']



def clean_mapped_trip_data(tripid):
    global df_cleaned
    
    trip_per_day = df[df['gst_trip_id'] == tripid].sort_values('processed_arrival_datetime')
    trip_per_day.loc[trip_per_day["delay_in_min"] <=0, "delay_in_min"] = 0
    
    trip_per_day['dim_lag'] = trip_per_day['delay_in_min'].shift(1) 
    trip_per_day['dim_lead'] = trip_per_day['delay_in_min'].shift(-1)

    trip_per_day['delay_in_min'] = trip_per_day.apply(lambda x: remove_anomaly(x,dateid), axis=1)

    # if count==0:
    #     df_cleaned = trip_per_day
    # else :
    df_cleaned = pd.concat([df_cleaned, trip_per_day])

dates = ['2021-09-06', '2021-09-07', '2021-09-08', '2021-09-09', '2021-09-10', '2021-09-11', '2021-09-12', '2021-09-13','2021-09-14',
'2021-09-15','2021-09-16','2021-09-17','2021-09-18','2021-09-19']
for j in [77]:
    # [1,2,3,4,5,6,7,8,9,10,11,12,13,15,16]+[17,18,19,20]+[21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]+[51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75]:
    print("start", j)
    for i in dates:
        df_cleaned = pd.DataFrame()
        df=pd.read_sql(f"""select *, min(processed_arrival_datetime) OVER(PARTITION BY (gst_trip_id, cd_date) ) AS start_time
        from mapped_data_latest m where route_id={j} and cd_date ='{i}' and direction_id={direction_id} order by start_time,gst_trip_id ,stop_sequence;""",engine)
        # print(df.head())
        if len(df)==0:
            print(f"No data for {i}")
            continue
        trips = df.gst_trip_id.unique()
        # print(trips)


        for trip in trips:
            clean_mapped_trip_data(trip)
        # df_cleaned
        # df_cleaned[df_cleaned['arrival_time'] > '05:18:39']
        df_cleaned.loc[df_cleaned['delay_in_min']>60,"issue"]="Mode not available"
        df_cleaned["interplolated_delay_in_min"]=df_cleaned['delay_in_min']
        df_cleaned.loc[df_cleaned['interplolated_delay_in_min']>60,"interplolated_delay_in_min"]=60

        # print(df_cleaned.head())
        df_cleaned.to_sql('corrected_mapped_data_latest',engine,if_exists='append',index=False)
    print("end", j)