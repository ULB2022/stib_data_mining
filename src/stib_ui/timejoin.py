"""Main logic engine for complete interface."""
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import pyarrow as pa
from sqlalchemy import create_engine

pd.options.plotting.backend = "plotly"
engine = create_engine(f"postgresql://localhost:5432/dm")


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


def get_dates(line_id, stop_id, direction):
    sql_dates = f"""select distinct(cast(cd_date as TEXT)) from "joinedsttcdebug_test" where route_id={line_id} and stop_id~'{stop_id}' and direction_id={direction} and cd_date>'2021-9-6';"""
    df_dates = pd.read_sql(sql_dates, engine)
    dt_dates = list(df_dates["cd_date"])
    return dt_dates


def get_line():
    sql_line = f"""select route_id,route_Short_name from "gtfs3Sept_routes";"""
    df_line = pd.read_sql(sql_line, engine)
    list_line = list(df_line[["route_id", "route_short_name"]])
    return list_line


def read_mapped_data(route_id=6, cd_date="2021-09-18", direction=0, stop_id="8162"):
    sql_gtfs = f"""select * from corrected_mapped_data_latest where route_id={route_id} and cd_date = '{cd_date}' and direction_id={direction} and stop_id ~'^[0]*{stop_id}[A-Z]*$' order by processed_arrival_datetime;"""
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


def inter_arrival_mapped_datetime(dataframe):
    dataframe["lagging_time"] = dataframe["mapped_time"].shift(1)
    dataframe["real_inter_arrival_time"] = dataframe.apply(
        lambda x: (x["mapped_time"] - x["lagging_time"])
        if x["lagging_time"] != np.nan
        else 0,
        axis=1,
    )
    dataframe["real_inter_arrival_time"] = (
        dataframe["real_inter_arrival_time"]
        .fillna(pd.Timedelta(seconds=0))
        .astype("timedelta64[m]")
        .astype(int)
    )
    dataframe = dataframe.drop(["lagging_time"], axis=1)
    return dataframe


def r(sql):
    data = pd.read_sql(sql, engine)
    return data


def calculate_ewt_for_stop(df):
    df_cluster_ewt = pd.DataFrame(
        columns=["cluster", "start_time", "end_time", "regularity", "swt", "awt", "ewt"]
    )
    clusters = df["cluster_id"].unique()
    df["iat2"] = df["inter_arrival_time"] ** 2
    df["aiat2"] = df["real_inter_arrival_time"] ** 2
    df.to_csv("delete_me.csv")
    for cluster in clusters:
        df_sliced = df[(df["cluster_id"] == cluster)]
        regularity = df_sliced["regularity"].unique()[0]
        if df_sliced.empty:
            df_cluster_ewt = pd.concat(
                [
                    df_cluster_ewt,
                    [
                        cluster,
                        min(df_sliced["processed_arrival_datetime"]),
                        max(df_sliced["processed_arrival_datetime"]),
                        regularity,
                        0,
                        0,
                        0,
                    ],
                ]
            )
        elif regularity == 1:
            swt = sum(df_sliced["iat2"]) / (
                2 * sum(df_sliced["inter_arrival_time"])
                if sum(df_sliced["inter_arrival_time"]) != 0
                else 1
            )
            awt = (
                sum(df_sliced["aiat2"])
                / (
                    2 * sum(df_sliced["real_inter_arrival_time"])
                    if sum(df_sliced["real_inter_arrival_time"]) != 0
                    else 1
                )
                if sum(df_sliced["real_inter_arrival_time"]) > 0
                else 10000
            )
            ewt = awt - swt if (awt > swt) else 0
            df_cluster_temp = pd.DataFrame(
                [
                    [
                        cluster,
                        min(df_sliced["processed_arrival_datetime"]),
                        max(df_sliced["processed_arrival_datetime"]),
                        regularity,
                        swt,
                        awt,
                        ewt,
                    ]
                ],
                columns=[
                    "cluster",
                    "start_time",
                    "end_time",
                    "regularity",
                    "swt",
                    "awt",
                    "ewt",
                ],
            )
            df_cluster_ewt = pd.concat([df_cluster_ewt, df_cluster_temp])
        else:
            df_cluster_temp = pd.DataFrame(
                [
                    [
                        cluster,
                        min(df_sliced["processed_arrival_datetime"]),
                        max(df_sliced["processed_arrival_datetime"]),
                        regularity,
                        np.nan,
                        np.nan,
                        np.nan,
                    ]
                ],
                columns=[
                    "cluster",
                    "start_time",
                    "end_time",
                    "regularity",
                    "swt",
                    "awt",
                    "ewt",
                ],
            )
            df_cluster_ewt = pd.concat([df_cluster_ewt, df_cluster_temp])
    return df_cluster_ewt


def add_marker(fig, route_id, direction, date):
    day = date.weekday()
    selected_date_cat = (
        "WED" if day == 2 else "SAT" if day == 5 else "SUN" if day == 6 else "EEKDAY"
    )
    date_string = date.strftime("%Y-%m-%d")
    sql = f"""select "min"-'1970-01-01'::date+'{date_string}'::date as head,"max"-'1970-01-01'::date+'{date_string}'::date as tail,regularity_interval from cluster_intervals where route_id={route_id} and direction_id={direction} and date_cat='{selected_date_cat}'"""
    data = r(sql)
    for index, row in data.iterrows():
        fig.add_vrect(
            x0=row["head"],
            x1=row["tail"],
            fillcolor="red" if row["regularity_interval"] == 0 else None,
            opacity=0.2,
            annotation_text="regular"
            if row["regularity_interval"] == 1
            else "punctual",
            annotation=dict(font_size=20, font_family="Times New Roman"),
        )
    return fig


def mark_cluster(dataframe, route_id, direction, date):
    day = date.weekday()
    selected_date_cat = (
        "WED" if day == 2 else "SAT" if day == 5 else "SUN" if day == 6 else "EEKDAY"
    )
    date_string = date.strftime("%Y-%m-%d")
    sql = f"""select "min"-'1970-01-01'::date+'{date_string}'::date as head,"max"-'1970-01-01'::date+'{date_string}'::date as tail,regularity_interval from cluster_intervals where route_id={route_id} and direction_id={direction} and date_cat='{selected_date_cat}';"""
    data = r(sql)
    size = len(data)
    minimum, maximum = data["head"].min(), data["tail"].max()

    dataframe = dataframe.assign(cluster_id=None, regularity=0)
    cluster_id = []
    regularity = []
    for index, row in dataframe.iterrows():
        base_data = row["processed_arrival_datetime"]
        i = -1
        if minimum > base_data:
            i = 0
        elif maximum < base_data:
            i = size - 1
        else:
            i = data[(data["head"] <= base_data) & (data["tail"] > base_data)].index[0]

        cluster_id.append(i)
        regularity.append(data.iloc[i]["regularity_interval"])
    dataframe["cluster_id"] = cluster_id
    dataframe["regularity"] = regularity
    return dataframe


def map_gtfs(
    route_id=7, stop_id=5253, direction=0, cd_date="2021-09-18", content="delay"
):
    print(f"Starting for stop id {stop_id} and direction {direction}")
    db_date = datetime.strptime(cd_date, "%Y-%m-%d")
    str_date = db_date.strftime("%Y-%-m-%-d")
    cd_date_gtfs = db_date.date()

    gtfs = read_mapped_data(
        route_id=route_id, cd_date=str_date, direction=direction, stop_id=stop_id
    )

    gtfs = inter_arrival_datetime(gtfs)
    gtfs = inter_arrival_mapped_datetime(gtfs)

    # gtfs["mapped_time"] = gtfs["mapped_time"].array.astype("datetime64[ns]")
    if content == "ewt":
        gtfs = mark_cluster(gtfs, route_id=route_id, direction=direction, date=db_date)
        ewt = calculate_ewt_for_stop(gtfs)
        ewt["regularity"] = ewt["regularity"].apply(
            lambda x: "Regular" if x == 1 else "Punctual"
        )
        return ewt
    gtfs.loc[gtfs["delay_in_min"] <= 0, "delay_in_min"] = 0
    if content == "table":
        return gtfs
    # Graph it out
    fig = None
    gtfs.info()
    if content == "headway":
        inter_arrival_df = gtfs.loc[
            :, ["processed_arrival_datetime", "inter_arrival_time"]
        ].copy()
        inter_arrival_df["type"] = "scheduled"
        real_arrival_df = gtfs.loc[
            :, ["processed_arrival_datetime", "real_inter_arrival_time"]
        ].copy()
        real_arrival_df = real_arrival_df.rename(
            columns={"real_inter_arrival_time": "inter_arrival_time"}
        )
        real_arrival_df["type"] = "real"
        result = [inter_arrival_df, real_arrival_df]
        final_df = pd.concat(result)
        fig = px.bar(
            final_df,
            x="processed_arrival_datetime",
            y="inter_arrival_time",
            color="type",
            labels={
                "inter_arrival_time": "Inter Arrival Time",
                "processed_arrival_datetime": "Processed Arrival Datetime",
            },
            height=400,
            color_discrete_map={"real": "red", "scheduled": "green"},
        )
        fig.update_layout(
            yaxis_range=[0, 50],
            template="plotly_white",
            title=f"Headway {route_id} {stop_id} {direction}",
        )
        fig.add_hline(y=12, line_width=1)
    elif content == "delay":
        fig = gtfs.plot.bar(
            x="processed_arrival_datetime",
            y="interplolated_delay_in_min",
            color="delay_in_min",
            # title=f"{route_id} {stop_id} {direction} Delay",
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={"mapped_time": "Mapped time"},
            width=15,
        )
        fig.update_layout(
            template="plotly_white", title=f"Delay {route_id} {stop_id} {direction}"
        )

        fig.add_hline(y=4, line_width=1)
    fig = add_marker(fig, route_id, direction, db_date)
    return fig
