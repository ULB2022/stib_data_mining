import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import pandas as pd
from datetime import timedelta, datetime

DB = "dm"
engine = create_engine(f"postgresql://localhost:5432/{DB}")
fig, ax = plt.subplots()
plt.style.use("fivethirtyeight")
plt.figure(figsize=(100, 10))
sql ="""select 
    processed_arrival_datetime,
     EXTRACT(EPOCH FROM (processed_arrival_datetime - LAG(processed_arrival_datetime) OVER (
        ORDER BY processed_arrival_datetime
    )))/60 as time_diff
from "joinedsttcdebug_test" a
where route_id = '20'
    and stop_id = '1748'
    and direction_id = '1'
    and cd_date = '2021-08-23'
order by a.processed_arrival_datetime"""
df = pd.read_sql(sql, engine)
df.head()
df = df.set_index("processed_arrival_datetime")
# Labelling the axes and setting a
# title
plt.xlabel("Date")
plt.ylabel("Values")
plt.title("Bar Plot of 'A'")
df['xyz'] = df['time_diff'].apply(lambda x: str(x).lower())

a=plt.bar(df.index, df["time_diff"],  align='edge',width=0.001)
# a=plt.step(df.index, df["time_diff"], drawstyle='steps', label=list(df['xyz']))
plt.plot(df.index, df["time_diff"], 'o--', color='grey', alpha=0.3)
plt.bar_label(a,labels= df['xyz'],label_type='edge')
plt.show()