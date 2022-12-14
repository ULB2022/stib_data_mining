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



# -

df_real = None
df_gtfs = None

def read_data_from_db(lineid=7,route_id=6,cd_date="2021-09-18"):
    global df_real
    global df_gtfs
    t= datetime.strptime(cd_date, '%Y-%m-%d')
    print("here")
    #Adding 7200 to put it in local time and correlate date
    logger.info(f"""Read real time data for line {lineid}""")
    sql_real = f"""select date_time+7200000 as local_time,* from realtimedirection where lineid={lineid}"""
    df_real = pd.read_sql(sql_real,engine)
    print(df_real.head())
    logger.info(f"completed real time reading data for line {lineid}")
    print("All done")


    logger.info(f"Read gtfs data for line {route_id}")
    sql_gtfs = f"""select * from "joinedsttcdebug_test" where route_id='{route_id}' and cd_date='{cd_date}'"""
    df_gtfs = pd.read_sql(sql_gtfs,engine)
    logger.info(f"completed gtfs reading data for line {route_id}")

    df_real["dt"] = pd.to_datetime(df_real['local_time'], unit='ms')
    print(df_real["dt"].min(),df_real["dt"].max())
    # df_real.count()
    # df_real.head()

def get_dates(line_id,stop_id,direction):
    sql_dates = f"""select distinct(cast(cd_date as TEXT)) from "joinedsttcdebug_test" where route_id={line_id} and stop_id='{stop_id}' and direction_id={direction};"""
    df_dates=pd.read_sql(sql_dates,engine)
    dt_dates = list(df_dates['cd_date'])
    print(dt_dates)
    return dt_dates


def get_line():
    sql_dates = f"""select route_id,route_Short_name from "gtfs3Sept_routes";"""
    df_dates=pd.read_sql(sql_dates,engine)
    dt_dates = list(df_dates[['route_id','route_short_name']])
    return dt_dates


# stop_id = 8071
# # stop_id=8081
# direction = 1

# # Process all real time data

#Get Real time data
# df_real.to_parquet("real25.parquet")


def map_gtfs(stop_id="5253",stop_name="CAVELL", direction=0,cd_date="2021-09-18", send_dataframe = False):
    logger.info(f"Starting for stop id {stop_id} and direction {direction}")
    t= datetime.strptime(cd_date, '%Y-%m-%d')
    cd_date_gtfs = t.date()
    delta =timedelta(days=1)
    print(df_real.head())
    # Filter Real time data
    real=df_real[(df_real['start']==stop_name) & (df_real['direction']==direction) & (df_real["dt"]>=t) & (df_real["dt"]<=t+delta+delta)].sort_values('date_time').drop_duplicates(subset=['date_time'])
    print("real",real.head(10))
    # Real time processing ended
    print(real["dt"])

    # GTFS time data
    gtfs=df_gtfs[(df_gtfs['direction_id']==direction) & (df_gtfs['cd_date']==cd_date_gtfs) & (df_gtfs['stop_id']==str(stop_id))].sort_values(['processed_arrival_datetime'])
    # GTFS processing ended
    print("gtfs",gtfs.head())
    #Add columns needed for mapping
    gtfs['mapped_time']=None
    gtfs['distance'] = 0
    # gtfs.to_csv(f'data/gtfs_{stop_name}_{stop_id}.csv')
    # real.to_csv(f"data/real_{stop_name.replace(' ', '_')}_{stop_id}.csv")

    #loop to get the mapping with gtfs
    # Handled cases
    #   1. No time should be mapped twice
    #   2. Sequential mapping is done
    # print(gtfs.count())
    # print(real.count())
    # input()
    last_mapped_time=datetime(2019,1,1)
    for index, row in gtfs.iterrows():
        temp_mapped_time = real[(real['dt']>=row['processed_arrival_datetime']) & (real['dt']>last_mapped_time)]['dt'].min()
        # gtfs.at[index, 'distance'] = real[real['dt']==temp_mapped_time]['distancefrompoint']
        gtfs.at[index, 'mapped_time'] =temp_mapped_time
        last_mapped_time = row['mapped_time'] = temp_mapped_time
        # print(temp_mapped_time)
        
    # Needed to convert array to datetime
    print(gtfs['mapped_time'])
    gtfs['mapped_time'] = gtfs['mapped_time'].array.astype("datetime64[ns]")
    

    #Creating extra information for graphing
    gtfs["delay"] = gtfs['mapped_time']-gtfs['processed_arrival_datetime']
    gtfs["delay_in_secs"] = gtfs["delay"].astype('timedelta64[s]').astype(int)
    gtfs["delay_in_min"] = gtfs["delay"].astype('timedelta64[m]')
    # gtfs['base_time_in_min']= (gtfs["processed_arrival_datetime"] - t).astype('timedelta64[m]').astype(int)
    # gtfs.to_csv(f'data/gtfs_{stop_name}_{stop_id}.csv')
    if send_dataframe:
        return gtfs
    logger.info("Staring server for data")
    # Graph it out
    
    fig1 = gtfs[["processed_arrival_datetime","delay_in_secs"]].plot.bar(x='processed_arrival_datetime',y='delay_in_secs',color="delay_in_secs", color_continuous_scale=px.colors.sequential.Viridis)
    # fig = px.bar(gtfs, x='processed_arrival_datetime', y='delay_in_secs',color="delay_in_secs", color_continuous_scale=px.colors.sequential.Viridis)
    # fig = px.bar(gtfs, x='processed_arrival_datetime', y='delay_in_secs').update_traces(mode='lines+markers')
    # fig1.show()
    # fig1.update_traces(width=5)
    fig1.add_hline(y=30)
    fig1.add_hrect(y0=30, y1=1200, line_width=0, fillcolor="red", opacity=0.2)
    print("I reached here")
    return fig1




# lineid =1
# route_id = 2
# read_data_from_db(lineid=lineid, route_id=route_id)



all_stops = [(8011,"DE BROUCKERE"),
(8021,"GARE CENTRALE"),
(8031,"PARC"),
(8041,"ARTS-LOI"),
(8051,"MAELBEEK"),
(8061,"SCHUMAN"),
(8071,"MERODE"),
(8081,"MONTGOMERY"),
(8091,"JOSEPH.-CHARLOTTE"),
(8101,"GRIBAUMONT"),
(8111,"TOMBERG"),
(8121,"ROODEBEEK"),
(8131,"VANDERVELDE"),
(8141,"ALMA"),
(8151,"CRAINHEM"),
(8161,"STOCKEL"),
(8162,"STOCKEL"),
(8271,"SAINTE-CATHERINE"),
(8281,"COMTE DE FLANDRE"),
(8291,"ETANGS NOIRS"),
(8642,"ERASME"),
(8651,"EDDY MERCKX"),
(8661,"CERIA"),
(8671,"LA ROUE"),
(8681,"BIZET"),
(8691,"VEEWEYDE"),
(8701,"SAINT-GUIDON"),
(8711,"AUMALE"),
(8721,"JACQUES BREL"),
(8731,"GARE DE L'OUEST"),
(8741,"BEEKKANT")]

# for i in all_stops:
#     stop_id = 8071
#     # stop_id=8081
#     direction = 1
#     # stop_id = int(input("Enter stop id: "))
#     # direction = int(input("Enter direction: "))
#     logger.info(f"{i[0]}, {i[1]}")
#     input()
#     map_gtfs(stop_id=i[0],stop_name=i[1], direction=direction)
#     do_continue = int(input("For continuing type 1:"))
#     if do_continue!=1:
#         logger.info("Exiting")
#         break


# map_gtfs(stop_id=8071,stop_name="MERODE", direction=1).show()


# read_data_from_db(lineid=7,route_id=6,cd_date="2021-09-18")

# map_gtfs(stop_id="5253",stop_name="CAVELL", direction=0,cd_date="2021-09-18", send_dataframe = False)