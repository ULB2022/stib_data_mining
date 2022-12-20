# %%
import csv
from sqlalchemy import create_engine
import pandas as pd
from datetime import timedelta,datetime
import configparser
import numpy as np
import plotly.express as px
pd.options.plotting.backend = "plotly"

from numpy import where
from numpy import unique
from matplotlib import pyplot
from matplotlib.pyplot import figure

# %%
config = configparser.ConfigParser()
config.read('../stib.config')

DB = config['db']['DB']
USERNAME = config["db"]["USERNAME"]
PASSWORD = config["db"]["PASSWORD"]
PORT = config["db"]["PORT"]

engine = create_engine(
    f'postgresql://{USERNAME}:{PASSWORD}@localhost:{PORT}/{DB}')


# %%
def runAll(df,route_id,direction):
    # %%
    table = pd.pivot_table(df, values='delay_in_min', index=['start_time','gst_trip_id'],
                        columns=['stop_sequence'])

    # %%
    threshold = 15 
    delays_trip_start = []
    pointer = 0
    f= open('fault.txt','a')
    nf= open('no_fault.txt','a')
    for i,x in table.iterrows():
        curr = []

        start_time = i[0]
        trip_id = i[1]

        ls = list(x.items())
        l = x.count()
        
        start,j = 0,0
        mapping = []
        fault = False

        while j < l:
            if ls[j][1] >= threshold:
                j += 1
            else:
                if j != start:
                    if j - start >= 3:
                        fault = True
                    mapping.append([start,j])
                j += 1
                start = j

        print(f"{pointer} {start_time} {trip_id} {fault} {mapping}", file=f if fault else nf)
        if fault:
            delays_trip_start.append([pointer,start_time,trip_id,route_id,mapping])
        pointer = pointer +1
        
        print(delays_trip_start[:3])
    f.close()
    nf.close()
    # %%
    ans = [['Hello','Hello','Hello','Hello','Hello']]
    for i in range(0,len(delays_trip_start)):
        if i!=0 and delays_trip_start[i][0]-1!=delays_trip_start[i-1][0]:
            if ans[-1][0]!='Hello':
                ans.append(['Hello','Hello','Hello','Hello','Hello'])
        if i+2<len(delays_trip_start) and delays_trip_start[i][0]+2==delays_trip_start[i+2][0]:
            ans.append(delays_trip_start[i])
        elif i-1>=0 and i+1<len(delays_trip_start) and delays_trip_start[i][0]+1==delays_trip_start[i+1][0] and delays_trip_start[i][0]-1==delays_trip_start[i-1][0]:
            ans.append(delays_trip_start[i])
        elif i-2>0 and delays_trip_start[i][0]-2==delays_trip_start[i-2][0]:
            ans.append(delays_trip_start[i])
    ans.append(['Hello','Hello','Hello','Hello','Hello'])
    print(ans[:3])

    # %%
    myFile = open('sequentialDelays.csv', 'w')
    writer = csv.writer(myFile)
    writer.writerow(['Index', 'Time','Trip', 'Route','Mapping'])
    for data_list in ans:
        writer.writerow(data_list)
    myFile.close()

    # %%
    df = pd.read_csv('sequentialDelays.csv')

    # %%
    final_ans = []
    ans = []
    base = []
    trips = []
    x,y=None,None
    for ind, rows in df.iterrows():
        if rows['Index'] != 'Hello':
            t=rows['Trip']
            a=eval(rows['Mapping'])
            currSet = eval(rows['Mapping'])
            data = []
            for i in a:
                data+= list(range(i[0],i[1]))
            base = list(set(base).intersection(set(data)))
            trips.append(t)
            y=rows['Time']
        else:
            if ind!=0:
                # ans.append([t,base])
                final_ans.append([route_id,direction,base,[x,y],trips])
                # print(trips)
                # print(x,y)
                # print(base)
                # print(ans)
            if ind==len(df)-1:
                final_ans.append([route_id,direction,base,[x,y],trips])
                break
            b=df.iloc[ind+1]['Mapping']
            # print(df)
            a=eval(b)
            data = []
            for i in a:
                data += list(range(i[0],i[1]))
            trips= []        
            x=df.iloc[ind+1]['Time']
            y=df.iloc[ind+1]['Time']
            base=data

    myFile = open('propagationDelays.csv', 'a')
    writer = csv.writer(myFile)
    writer.writerow(['route','direction','mapping','start_end_time','trip_id'])
    for data_list in final_ans:
        writer.writerow(data_list)
    myFile.close()

print('Starting to run this code...............')

dates = ['2021-09-06','2021-09-07', '2021-09-08', '2021-09-09', '2021-09-10',
'2021-09-11', '2021-09-12', '2021-09-13','2021-09-14',
'2021-09-15','2021-09-16','2021-09-17','2021-09-18','2021-09-19']

lines = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98]

for k in lines:
    for i in dates:
        for j in [0,1]:
            sql= f"select * from corrected_mapped_data_latest where route_id={k} and cd_date='{i}' and direction_id={j};"
            
            df = pd.read_sql(sql, engine)
            print(df.head())
            runAll(df,k,j)
            print(f'Running for line - {k}, date - {i}, direction - {j}')