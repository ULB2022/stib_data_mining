import json
import os

import pandas as pd
from json_normalize import json_normalize
from sqlalchemy import create_engine

TO_SQL = True
CLEAN_UP = False
WORK_DIR = "/Users/Licious/Downloads/Project Data-20221102"
os.chdir(WORK_DIR)
OUTPUT_DIR = "/Users/Licious/project/ulb/datamining"
TIMETABLES_DIR = ["gtfs3Sept", "gtfs23Sept"]

engine = None
DB = "dm"
if TO_SQL:
    engine = create_engine(f'postgresql://localhost:5432/{DB}')
else:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def cleanup():
    if engine and CLEAN_UP:
        with engine.connect() as con:
            con.execute("DROP SCHEMA public CASCADE;")
            con.execute("CREATE SCHEMA public;")
            con.execute("GRANT ALL ON SCHEMA public TO postgres;")
            con.execute("GRANT ALL ON SCHEMA public TO public;")
    elif CLEAN_UP:
        os.rmdir(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_vehicle_positions():
    if not TO_SQL:
        os.makedirs(f"{OUTPUT_DIR}/vechile_positions")
    all_files = os.listdir()
    for i in all_files:
        if not i.startswith("vehiclePosition"):
            continue
        print(i)
        with open(i, "r") as read_file:
            data = json.load(read_file)
            normal_json = json_normalize(data)
            df = pd.DataFrame(normal_json)
            if TO_SQL:
                df["file"] = i
                df.to_sql("vechile_positions", engine, if_exists='append')
            else:
                df.to_csv(
                    f"{OUTPUT_DIR}/vechile_positions/{i.split('.')[0]}.csv")


def load_timetables():
    for t_dir in TIMETABLES_DIR:
        all_files = os.listdir(t_dir)
        if not TO_SQL:
            os.makedirs(f"{OUTPUT_DIR}/{t_dir}")
        for files in all_files:
            df = pd.read_csv(f"{t_dir}/{files}")
            if TO_SQL:
                table_name = f"{t_dir}_{files.split('.')[0]}"
                print(f"{t_dir} and {files}  in table {table_name}")
                df.to_sql(table_name, engine, if_exists='append')
            else:
                print(
                    f"{t_dir} and {files} in file ${OUTPUT_DIR}/{t_dir}/{files.split('.')[0]}.csv")
                df.to_csv(f"{OUTPUT_DIR}/{t_dir}/{files.split('.')[0]}.csv")


cleanup()
load_vehicle_positions()
load_timetables()
