from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime

engine = create_engine('postgresql://localhost:5432/dm')
data = pd.read_sql('select * from "gtfs23Sept_stop_times"',engine)


# Process arrival time 23
print("Arrival time 23")
data['processed_arrival_time'] = data.apply(lambda x: f"{str(int(x['arrival_time'].split(':')[0])%24)}:{':'.join(x['arrival_time'].split(':')[1:])}", axis=1)
data['processed_arrival_date'] = data.apply(lambda x: "24/09/2021" if int(x['arrival_time'].split(':')[0])>23 else "23/09/2021", axis=1)
data['processed_arrival_datetime'] = data.apply(lambda x: datetime.strptime(f"{x['processed_arrival_date']} {x['processed_arrival_time']}","%d/%m/%Y %H:%M:%S"), axis=1)
# Process departure time 23
print("Departure time 23")
data['processed_departure_time'] = data.apply(lambda x: f"{str(int(x['departure_time'].split(':')[0])%24)}:{':'.join(x['departure_time'].split(':')[1:])}", axis=1)
data['processed_departure_date'] = data.apply(lambda x: "24/09/2021" if int(x['departure_time'].split(':')[0])>23 else "23/09/2021", axis=1)
data['processed_departure_datetime'] = data.apply(lambda x: datetime.strptime(f"{x['processed_departure_date']} {x['processed_departure_time']}","%d/%m/%Y %H:%M:%S"), axis=1)
print("Table 23")

data.to_sql("stoptimes23", engine)


data = pd.read_sql('select * from "gtfs3Sept_stop_times"',engine)

print("Arrival time 3")
data['processed_arrival_time'] = data.apply(lambda x: f"{str(int(x['arrival_time'].split(':')[0])%24)}:{':'.join(x['arrival_time'].split(':')[1:])}", axis=1)
data['processed_arrival_date'] = data.apply(lambda x: "04/09/2021" if int(x['arrival_time'].split(':')[0])>23 else "03/09/2021", axis=1)
data['processed_arrival_datetime'] = data.apply(lambda x: datetime.strptime(f"{x['processed_arrival_date']} {x['processed_arrival_time']}","%d/%m/%Y %H:%M:%S"), axis=1)
# Process departure time 3
print("Departure time 3")
data['processed_departure_time'] = data.apply(lambda x: f"{str(int(x['departure_time'].split(':')[0])%24)}:{':'.join(x['departure_time'].split(':')[1:])}", axis=1)
data['processed_departure_date'] = data.apply(lambda x: "04/09/2021" if int(x['departure_time'].split(':')[0])>23 else "03/09/2021", axis=1)
data['processed_departure_datetime'] = data.apply(lambda x: datetime.strptime(f"{x['processed_departure_date']} {x['processed_departure_time']}","%d/%m/%Y %H:%M:%S"), axis=1)
print("Table 3")

data.to_sql("stoptimes3", engine)
print("complete")