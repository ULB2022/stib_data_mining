# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3.10.8 ('python3.10')
#     language: python
#     name: python3
# ---

#  Setting up logger
import logging.config
import logging
import yaml

with open('logging.yml','rt') as f:
        config=yaml.safe_load(f.read())
        f.close()
logging.config.dictConfig(config)
logger=logging.getLogger(__name__)
logger.info("Logging will start")
#  Logger setup



from sqlalchemy import create_engine
import pandas as pd
import pyarrow as pa
from datetime import timedelta,datetime,date
import plotly.express as px
pd.options.plotting.backend = "plotly"
engine = create_engine(f'postgresql://localhost:5432/dm')


# +
# date under consideration

cd_date = '2021-09-12'
t= datetime.strptime(cd_date, '%Y-%m-%d')
cd_date_gtfs = t.date()
delta =timedelta(days=1)

# -

df_real = None
df_gtfs = None

def read_data_from_db(lineid,route_id):
    global df_real
    global df_gtfs

    #Adding 7200 to put it in local time and correlate date
    logger.info(f"Read real time data for line {lineid}")
    sql_real = f"""select date_time+7200000 as local_time,* from realtimedirection where lineid={lineid}"""
    df_real = pd.read_sql(sql_real,engine)
    logger.info(f"completed real time reading data for line {lineid}")


    logger.info(f"Read gtfs data for line {route_id}")
    sql_gtfs = f"""select * from "joinedsttcdebug_test" where route_id='{route_id}' and cd_date='{cd_date}'"""
    df_gtfs = pd.read_sql(sql_gtfs,engine)
    logger.info(f"completed gtfs reading data for line {route_id}")

    df_real["dt"] = pd.to_datetime(df_real['local_time'], unit='ms')
    # df_real.count()
    # df_real.head()





# stop_id = 8071
# # stop_id=8081
# direction = 1

# # Process all real time data

#Get Real time data
# df_real.to_parquet("real25.parquet")


def map_gtfs(stop_id, direction):
    print("I am here")
    logger.info(f"Starting for stop id {stop_id} and direction {direction}")
    # Filter Real time data
    real=df_real[(df_real['pointid']==stop_id) & (df_real['direction']==direction) & (df_real["dt"]>=t) & (df_real["dt"]<=t+delta+delta)].sort_values('date_time',ascending=False)
    real.head(10)
    # Real time processing ended


    # GTFS time data
    gtfs=df_gtfs[(df_gtfs['direction_id']==direction) & (df_gtfs['cd_date']==cd_date_gtfs) & (df_gtfs['stop_id']==str(stop_id))].sort_values(['processed_arrival_datetime'])
    # GTFS processing ended

    #Add columns needed for mapping
    gtfs['mapped_time']=None
    gtfs['distance'] = 0

    #loop to get the mapping with gtfs
    # Handled cases
    #   1. No time should be mapped twice
    #   2. Sequential mapping is done
    last_mapped_time=datetime(2019,1,1)
    for index, row in gtfs.iterrows():
        temp_mapped_time = real[(real['dt']>=row['processed_arrival_datetime']) & (real['dt']>last_mapped_time)]['dt'].min()
        gtfs.at[index, 'distance'] = real[real['dt']==temp_mapped_time]['distancefrompoint']
        gtfs.at[index, 'mapped_time'] =temp_mapped_time
        last_mapped_time = row['mapped_time'] = temp_mapped_time
        
    # Needed to convert array to datetime
    gtfs['mapped_time'] = gtfs['mapped_time'].array.astype("datetime64[ns]")


    #Creating extra information for graphing
    gtfs["delay"] = gtfs['mapped_time']-gtfs['processed_arrival_datetime']
    gtfs["delay_in_secs"] = gtfs["delay"].astype('timedelta64[s]').astype(int)
    gtfs["delay_in_min"] = gtfs["delay"].astype('timedelta64[m]')
    gtfs['base_time_in_min']= (gtfs["processed_arrival_datetime"] - t).astype('timedelta64[m]').astype(int)

    logger.info("Staring server for data")
    # Graph it out
    fig1 = gtfs[["processed_arrival_datetime","delay_in_secs"]].plot.bar(x='processed_arrival_datetime',y='delay_in_secs',color="delay_in_secs", color_continuous_scale=px.colors.sequential.Viridis)
    fig1.show()




lineid =1
route_id = 2
read_data_from_db(lineid=lineid, route_id=route_id)


for i in range(5):
    stop_id = 8071
    # stop_id=8081
    direction = 1
    stop_id = int(input("Enter stop id: "))
    direction = int(input("Enter direction: "))
    map_gtfs(stop_id=stop_id, direction=direction)
    do_continue = int(input("For continuing type 1:"))
    if do_continue!=1:
        logger.info("Exiting")
        break

