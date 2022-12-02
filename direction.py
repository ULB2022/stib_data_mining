from sqlalchemy import create_engine
import pandas as pd
from datetime import timedelta,datetime
import json
engine = create_engine(f'postgresql://localhost:5432/dm')

stop_mapping = {}
manual_data ={}
manual_data[(1,"VANDERVELDE","ERASME")]=1
manual_data[(1,"ROODEBEEK","ERASME")]=1
manual_data[(1,"TOMBERG","ERASME")]=1
manual_data[(1,"ALMA","ERASME")]=1
manual_data[(1,"GRIBAUMONT","ERASME")]=1
manual_data[(1,"JOSEPH.-CHARLOTTE","ERASME")]=1
manual_data[(1,"MONTGOMERY","ERASME")]=1
manual_data[(1,"MERODE","ERASME")]=1
manual_data[(1,"CRAINHEM","ERASME")]=1
manual_data[(1,"SCHUMAN","ERASME")]=1
manual_data[(1,"MAELBEEK","ERASME")]=1
manual_data[(1,"PARC","ERASME")]=1
manual_data[(1,"GARE CENTRALE","ERASME")]=1
manual_data[(1,"SAINTE-CATHERINE","ERASME")]=1
manual_data[(1,"COMTE DE FLANDRE","ERASME")]=1
manual_data[(1,"ETANGS NOIRS","ERASME")]=1
manual_data[(1,"BEEKKANT","ERASME")]=1
manual_data[(1,"ARTS-LOI","ERASME")]=1
manual_data[(1,"JACQUES BREL","ERASME")]=1
manual_data[(1,"GARE CENTRALE","DELTA")]=0
manual_data[(1,"MERODE","HERRMANN-DEBROUX")]=0
manual_data[(1,"SCHUMAN","HERRMANN-DEBROUX")]=0
manual_data[(2,"BELGICA","ROI BAUDOUIN")]=1
manual_data[(2,"TRONE","ROI BAUDOUIN")]=1
manual_data[(2,"ARTS-LOI","ROI BAUDOUIN")]=1
manual_data[(2,"PORTE DE NAMUR","ROI BAUDOUIN")]=1
manual_data[(2,"LOUISE","ROI BAUDOUIN")]=1
manual_data[(2,"HOTEL DES MONNAIES","ROI BAUDOUIN")]=1
manual_data[(2,"GARE DU MIDI","ROI BAUDOUIN")]=1
manual_data[(2,"PORTE DE HAL","ROI BAUDOUIN")]=1
manual_data[(2,"CLEMENCEAU","ROI BAUDOUIN")]=1
manual_data[(2,"DELACROIX","ROI BAUDOUIN")]=1
manual_data[(2,"GARE DE L'OUEST","ROI BAUDOUIN")]=1
manual_data[(2,"BEEKKANT","ROI BAUDOUIN")]=1
manual_data[(2,"OSSEGHEM","ROI BAUDOUIN")]=1
manual_data[(5,"EDDY MERCKX","STOCKEL")]=0
manual_data[(5,"CERIA","STOCKEL")]=0
manual_data[(5,"LA ROUE","STOCKEL")]=0
manual_data[(5,"BIZET","STOCKEL")]=0
manual_data[(5,"VEEWEYDE","STOCKEL")]=0
manual_data[(5,"SAINT-GUIDON","STOCKEL")]=0
manual_data[(5,"AUMALE","STOCKEL")]=0
manual_data[(5,"JACQUES BREL","STOCKEL")]=0
manual_data[(5,"GARE DE L'OUEST","STOCKEL")]=0
manual_data[(5,"MERODE","STOCKEL")]=0
manual_data[(5,"SCHUMAN","STOCKEL")]=0
manual_data[(5,"PARC","STOCKEL")]=0
manual_data[(6,"HEYSEL","no station found")] = -1 # 8826
manual_data[(7,"ESPLANADE","CHAZAL")] = -1    # NO ESPLANADE on route 7
manual_data[(7,"ESPLANADE","BUYL")] = -1 # NO ESPLANADE on route 7
manual_data[(7,"ESPLANADE","no station found")] = -1
manual_data[(7,"DE WAND","no station found")] = -1
manual_data[(7,"ARAUCARIA","no station found")] = -1
# 9965
# 7 BUISSONNETS no station found
manual_data[(7,"BUISSONNETS","no station found")] = -1
#7 HEEMBEEK no station found
manual_data[(7,"HEEMBEEK","no station found")] = -1
#7 VAN PRAET no station found
manual_data[(7,"VAN PRAET","no station found")] = -1
#7 DOCKS BRUXSEL no station found
manual_data[(7,"DOCKS BRUXSEL","no station found")] = -1
#7 PRINC. ELISABETH no station found
manual_data[(7,"PRINC. ELISABETH","no station found")] = -1
#7 HOP. PAUL BRIEN no station found
manual_data[(7,"HOP. PAUL BRIEN","no station found")] = -1
#7 DEMOLDER no station found
manual_data[(7,"DEMOLDER","no station found")] = -1
#7 LOUIS BERTRAND no station found
manual_data[(7,"LOUIS BERTRAND","no station found")] = -1
#7 HELIOTROPES no station found
manual_data[(7,"HELIOTROPES","no station found")] = -1
#7 CHAZAL no station found
manual_data[(7,"CHAZAL","no station found")] = -1
#7 LEOPOLD III no station found
manual_data[(7,"LEOPOLD III","no station found")] = -1
#7 MEISER no station found
manual_data[(7,"MEISER","no station found")] = -1
#7 DIAMANT no station found
manual_data[(7,"DIAMANT","no station found")] = -1
#7 GEORGES HENRI no station found
manual_data[(7,"GEORGES HENRI","no station found")] = -1
#7 MONTGOMERY no station found
manual_data[(7,"MONTGOMERY","no station found")] = -1
#7 BOILEAU no station found
manual_data[(7,"BOILEAU","no station found")] = -1
#7 PETILLON no station found
manual_data[(7,"PETILLON","no station found")] = -1
#7 SAINT-LAMBERT no station found
manual_data[(7,"SAINT-LAMBERT","no station found")] = -1
#7 ARSENAL no station found
manual_data[(7,"ARSENAL","no station found")] = -1
#7 VUB no station found
manual_data[(7,"VUB","no station found")] = -1
#7 ETTERBEEK GARE no station found
manual_data[(7,"ETTERBEEK GARE","no station found")] = -1
#7 ROFFIAEN no station found
manual_data[(7,"ROFFIAEN","no station found")] = -1
#7 BUYL no station found
manual_data[(7,"BUYL","no station found")] = -1
#8 STEPHANIE no station found
manual_data[(8,"STEPHANIE","no station found")] = -1
#8 DEFACQZ no station found
manual_data[(8,"DEFACQZ","no station found")] = -1
#8 BAILLI no station found
manual_data[(8,"BAILLI","no station found")] = -1
#8 VLEURGAT no station found
manual_data[(8,"VLEURGAT","no station found")] = -1
#8 LEGRAND no station found
manual_data[(8,"LEGRAND","no station found")] = -1
#8 ABBAYE no station found
manual_data[(8,"ABBAYE","no station found")] = -1
#8 BUYL no station found
manual_data[(8,"BUYL","no station found")] = -1
#8 ULB no station found
manual_data[(8,"ULB","no station found")] = -1
#8 SOLBOSCH no station found
manual_data[(8,"SOLBOSCH","no station found")] = -1
#8 MARIE-JOSE no station found
manual_data[(8,"MARIE-JOSE","no station found")] = -1
#8 BRESIL no station found
manual_data[(8,"BRESIL","no station found")] = -1
#8 BOONDAEL GARE no station found
manual_data[(8,"BOONDAEL GARE","no station found")] = -1
#8 CAMBRE-ETOILE no station found
manual_data[(8,"CAMBRE-ETOILE","no station found")] = -1
# No direction found. Not possible to find
manual_data[(7,"HEYSEL","no station found")] = -1
# No direction found. Not possible to find
manual_data[(8,"LOUISE","no station found")] = -1



with open('line_processed.json', 'r') as f:
    all_lines = json.load(f)
    all_lines = all_lines['all_lines']
for line, variants in all_lines.items():
    v_sql =f"""select date_time::bigint, lineid::int,pointid::int, directionid::int,distancefrompoint::int,file from "vechile_positions" where lineid='{line}'"""
    v_data = pd.read_sql(v_sql,engine)
    all_combinations = v_data[['pointid', 'directionid']].drop_duplicates()

    all_stations = variants["0"]+variants["1"]
    point_ids = list(all_combinations['pointid'].unique())
    direction_ids = list(all_combinations['directionid'].unique())

    for i in set(point_ids+direction_ids):
        d=f"""select * from "gtfs3Sept_stops" where stop_id ~ '^0*{i}[A-Z]*$';"""
        df = list(set(pd.read_sql(d,engine)['stop_name']))
        try:
            stop_mapping[i]=df[0]
        except:
            print(i)
    v_data["start"]="No"
    v_data["end"]="No"
    for i,j in stop_mapping.items():
        v_data.loc[v_data['pointid'] == i, ['start']] = j
        v_data.loc[v_data['directionid'] == i, ['end']] = j
    # print(v_data.head())

    v_data["direction"] = -1
    last_station_0 =  variants["0"][-1]
    first_station_0 =  variants["0"][0]
    last_station_1 =  variants["1"][-1]
    first_station_1 =  variants["1"][0]
    count_last,count_not_last = 0,0
    print(v_data.count())
    for index, row in v_data.iterrows():
        d=-1
        point,last_stop=None,None
        try:
            point = stop_mapping[row["pointid"]]
        except:
            point = "no station found"
        try:
            last_stop = stop_mapping[row["directionid"]]
        except:
            last_stop = "no station found"
            if (int(line),point,last_stop) not  in manual_data:
                print("# No direction found. Not possible to find")
                manual_data[(int(line),point,last_stop)] = d
                print(row["directionid"])
                print(f"""manual_data[({line},"{point}","{last_stop}")] = -1""")
            v_data.at[ index, 'direction'] = d
            continue

        if last_stop==last_station_0:
            d=0
        elif last_stop==last_station_1:
            d=1
        elif point==first_station_0:
            d=0
        elif point==first_station_1:
            d=1
        elif (point in variants["0"]) and (point not in variants["1"] ):
            d = 0
        elif (point in variants["1"]) and (point not in variants["0"]):
            d = 1
        elif (last_stop in variants["0"]) and (last_stop not in variants["1"] ):
            d = 0
        elif (last_stop in variants["1"]) and (last_stop not in variants["0"]):
            d = 1
        else:
            if point in variants["0"] and last_stop in variants["0"] and variants["0"].index(point) < variants["0"].index(last_stop):
                d = 0
            elif point in variants["1"] and last_stop in variants["1"] and  variants["1"].index(point)< variants["1"].index(last_stop):
                d = 1
            elif (int(line),point,last_stop) in manual_data:
                d=manual_data[(int(line),point,last_stop)]
            else:
                d = -1
                manual_data[(int(line),point,last_stop)] = d
                print(f"""manual_data[({line},"{point}","{last_stop}")] = {d}""")
                print(f"""# {line} {point} {last_stop}""")
        v_data.at[index, 'direction'] = d
    print("Write in table")
    v_data.to_sql('realtimedirection',engine,if_exists='append', index=False)
    direction_distribution = v_data.groupby(['direction'])['direction'].count()
    print(direction_distribution)