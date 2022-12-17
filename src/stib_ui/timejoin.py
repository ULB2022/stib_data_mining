import numpy as np


from sqlalchemy import create_engine
import pandas as pd
import pyarrow as pa
from datetime import timedelta, datetime, date
import plotly.express as px

pd.options.plotting.backend = "plotly"
engine = create_engine(f"postgresql://localhost:5432/dm")


# +
# date under consideration

cd_date = "2021-09-12"


# -

df_real = None
df_gtfs = None


def read_data_from_db(lineid=7, route_id=6, cd_date="2021-09-18"):
    global df_real
    global df_gtfs
    t = datetime.strptime(cd_date, "%Y-%m-%d")
    # Adding 7200 to put it in local time and correlate date
    sql_real = f"""select date_time+7200000 as local_time,* from realtimedirection where lineid={lineid}"""
    df_real = pd.read_sql(sql_real, engine)

    sql_gtfs = f"""select * from "joinedsttcdebug_test" where route_id='{route_id}'"""
    df_gtfs = pd.read_sql(sql_gtfs, engine)

    df_real["dt"] = pd.to_datetime(df_real["local_time"], unit="ms")
    # df_real.count()
    # df_real.head()


def get_dates(line_id, stop_id, direction):
    sql_dates = f"""select distinct(cast(cd_date as TEXT)) from "joinedsttcdebug_test" where route_id={line_id} and stop_id~'{stop_id}' and direction_id={direction} and cd_date>'2021-9-6';"""
    df_dates = pd.read_sql(sql_dates, engine)
    dt_dates = list(df_dates["cd_date"])
    print(dt_dates)
    return dt_dates


def get_line():
    sql_line = f"""select route_id,route_Short_name from "gtfs3Sept_routes";"""
    df_line = pd.read_sql(sql_line, engine)
    list_line = list(df_line[["route_id", "route_short_name"]])
    return list_line


def read_mapped_data(route_id=6, cd_date="2021-09-18", direction=0, stop_id="8162"):
    sql_gtfs = f"""select * from mapped_data_latest where route_id={route_id} and cd_date = '{cd_date}' and direction_id={direction} and stop_id ~'^[0]*{stop_id}[A-Z]*$' order by processed_arrival_datetime;"""
    print(sql_gtfs)
    df_gtfs = pd.read_sql(sql_gtfs, engine)
    return df_gtfs


def inter_arrival_datetime(dataframe):
    dataframe["lagging_time"] = dataframe["processed_arrival_datetime"].shift(1)
    dataframe["inter_arrival_time"] = dataframe.apply(
        lambda x: (x["processed_arrival_datetime"] - x["lagging_time"])
        if x["lagging_time"] != np.nan
        else 0,
        axis=1,
    )
    dataframe["inter_arrival_time"] = (
        dataframe["inter_arrival_time"]
        .fillna(pd.Timedelta(seconds=0))
        .astype("timedelta64[m]")
        .astype(int)
    )
    dataframe = dataframe.drop(["lagging_time"], axis=1)
    return dataframe


def r(sql):
    data = pd.read_sql(sql, engine)
    return data


def add_marker(fig, route_id, direction, date):
    day = date.weekday()
    selected_date_cat = (
        "WED" if day == 2 else "SAT" if day == 5 else "SUN" if day == 6 else "WEEKDAY"
    )
    date_string = date.strftime("%Y-%m-%d")
    sql = f"""select "min"-'1970-01-01'::date+'{date_string}'::date as head,"max"-'1970-01-01'::date+'{date_string}'::date as tail,regularity_interval from cluster_intervals where route_id={route_id} and direction_id={direction} and date_cat='{selected_date_cat}' and method='Kmeans';"""
    data = r(sql)
    for index, row in data.iterrows():
        fig.add_vrect(
            x0=row["head"],
            x1=row["tail"],
            fillcolor="red" if row["regularity_interval"] == 0 else None,
            opacity=0.2,
            annotation_text="regular" if row["regularity_interval"] == 1 else "punctual",
            annotation=dict(font_size=20, font_family="Times New Roman"),
            # annotation_position="top",
        )
    return fig


def map_gtfs(
    route_id=7, stop_id=5253, direction=0, cd_date="2021-09-18", content="delay"
):
    print(f"Starting for stop id {stop_id} and direction {direction}")
    db_date = datetime.strptime(cd_date, "%Y-%m-%d")
    str_date = db_date.strftime("%Y-%-m-%-d")
    cd_date_gtfs = db_date.date()

    # delta =timedelta(days=1)
    print(route_id)
    gtfs = read_mapped_data(
        route_id=route_id, cd_date=str_date, direction=direction, stop_id=stop_id
    )

    print("all_data", direction, cd_date_gtfs, stop_id)
    gtfs = inter_arrival_datetime(gtfs)
    # gtfs["mapped_time"] = gtfs["mapped_time"].array.astype("datetime64[ns]")

    gtfs.loc[gtfs["delay_in_min"] <= 0, "delay_in_min"] = 0
    if content == "table":
        return gtfs
    # Graph it out
    fig = None
    if content == "headway":
        fig = gtfs[["processed_arrival_datetime", "inter_arrival_time"]].plot.bar(
            x="processed_arrival_datetime",
            y="inter_arrival_time",
            color="inter_arrival_time",
            width=100,
            color_continuous_scale=px.colors.sequential.Viridis,
        )
        # fig = px.bar(gtfs, x='processed_arrival_datetime', y='delay_in_secs',color="delay_in_secs", color_continuous_scale=px.colors.sequential.Viridis)
        # fig = px.bar(gtfs, x='processed_arrival_datetime', y='inter_arrival_time').update_traces(mode='lines+markers')
        # fig1.show()
        # fig.update_traces(width=5)
        fig.add_hline(y=0)
        fig.add_hrect(y0=12, y1=20, line_width=0, fillcolor="red", opacity=0.2)
    elif content == "delay":
        # [["processed_arrival_datetime", "delay_in_min", "mapped_time"]]
        fig = gtfs.plot.bar(
            x="processed_arrival_datetime",
            y="delay_in_min",
            color="delay_in_min",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={"mapped_time": "Mapped time"},
            width=15,
        )
        fig.add_hline(y=0)
        fig.add_hrect(y0=4, y1=20, line_width=0, fillcolor="red", opacity=0.2)
    fig = add_marker(fig, route_id, direction, db_date)
    return fig


# map_gtfs(route_id =58, stop_id=3921, direction=0,cd_date="2021-09-11").head()
