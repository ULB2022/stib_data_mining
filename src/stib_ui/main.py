import dash  # version 1.13.1

# import dash as dcc
from dash import dcc, dash_table, ctx
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc

# import dash as html
from dash import html
from dash.html import Label, Div
from dash.dependencies import Input, Output, ALL, State, MATCH, ALLSMALLER
import plotly.express as px
import pandas as pd
import numpy as np
from options import mode_line_mapping, line_stop_mapping, route_line_mapping
import timejoin
from map import map_maker
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Input, Output

import diskcache

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])

app.layout = html.Div(
    [
        html.Div(
            id="container1",
            style={"display": "flex"},
            children=[
                Div(
                    id="t-dropdown-parent",
                    children=[
                        Label("Select Transport"),
                        Dropdown(
                            list(mode_line_mapping.keys()),
                            list(mode_line_mapping.keys())[0],
                            searchable=True,
                            id="t-dropdown",
                        ),
                    ],
                    style={"width": "33%"},
                ),
                Div(
                    id="l-dropdown-parent",
                    children=[
                        Label("Select Line"),
                        Dropdown(
                            mode_line_mapping["T"],
                            mode_line_mapping["T"][0],
                            searchable=True,
                            id="l-dropdown",
                        ),
                    ],
                    style={"width": "33%"},
                ),
                Div(
                    id="d-dropdown-parent",
                    children=[
                        Label("Select Direction"),
                        Dropdown(
                            ["0", "1"],
                            "0",
                            id="d-dropdown",
                        ),
                    ],
                    style={"width": "33%"},
                ),
                Div(
                    id="s-dropdown-parent",
                    children=[
                        Label("Select Stop"),
                        Dropdown(
                            line_stop_mapping["all_lines"]["1"]["0"],
                            line_stop_mapping["all_lines"]["1"]["0"][0],
                            searchable=True,
                            id="s-dropdown",
                        ),
                    ],
                    style={"width": "33%"},
                ),
                Div(
                    id="date-dropdown-parent",
                    children=[
                        Label("Select Date"),
                        Dropdown(
                            ["2021-08-26", "2021-08-27"],
                            "2021-08-26",
                            searchable=True,
                            id="date-dropdown",
                        ),
                    ],
                    style={"width": "33%"},
                ),
                Div(
                    id="dummy_div",
                    style={"display": "None"},
                ),
            ],
        ),
        html.Div(
            children=[
                html.Button(
                    "Add Delay Graph",
                    id="add-graph",
                    n_clicks=0,
                    className="btn btn-primary",
                ),
                html.Button(
                    "Add Headway Graph",
                    id="add-graph-head",
                    n_clicks=0,
                    className="btn btn-primary",
                ),
                html.Button(
                    "Add Table", id="add-table", n_clicks=0, className="btn btn-light"
                ),
                html.Button(
                    "Add Map", id="add-map", n_clicks=0, className="btn btn-success"
                ),
            ],
            style={"text-align": "center"},
        ),
        html.Div(id="container", children=[], className="wrapper"),
    ]
)

# @app.callback(Output("dummy_div", "style"),inputs=[Input('date-dropdown', 'value')],
#                  state=[State('l-dropdown', 'value')],
#                 manager= long_callback_manager
# )
# def upload_data_for_line(cd_date,line):
#     print("date dropdown")
#     print(line,route_line_mapping[str(line)],cd_date)
#     timejoin.read_data_from_db(lineid=line,route_id=route_line_mapping[str(line)],cd_date=cd_date)
#     print("date derop dow")
#     return {"display": "None"}


@app.long_callback(
    output=[
        Output("l-dropdown", "options"),
        Output("s-dropdown", "options"),
        Output("date-dropdown", "options"),
        Output("s-dropdown", "value"),
        Output("date-dropdown", "value"),
    ],
    inputs=[
        dash.dependencies.Input("s-dropdown", "value"),
        dash.dependencies.Input("l-dropdown", "value"),
        dash.dependencies.Input("d-dropdown", "value"),
        #   dash.dependencies.Input('date-dropdown', 'value'),
        Input("t-dropdown", "value"),
    ],
    state=[
        State("date-dropdown", "value"),
        State("s-dropdown", "value"),
        State("t-dropdown", "value"),
    ],
    manager=long_callback_manager,
)
def change_my_dropdown_options(
    initial_stop,
    initial_line,
    initial_direction,
    initial_transport,
    date_value,
    stop_value,
    transport_value,
):
    # print(s,d,l,t)
    # print(initial_stop,initial_line,initial_direction,initial_transport,date_value,stop_value,transport_value)
    options = None
    lines = mode_line_mapping[initial_transport]
    dates = []
    stops = line_stop_mapping["all_lines"][str(initial_line)][initial_direction]
    if "t-dropdown" == ctx.triggered_id:
        lines = mode_line_mapping[initial_transport]
        stops = line_stop_mapping["all_lines"][str(initial_line)][initial_direction]
    elif "l-dropdown" == ctx.triggered_id:
        stops = line_stop_mapping["all_lines"][str(initial_line)][initial_direction]
        options = line_stop_mapping["all_lines"][str(initial_line)][initial_direction]
        # print("Hello I have initiated the bomb")
    elif "s-dropdown" == ctx.triggered_id:
        stops = line_stop_mapping["all_lines"][str(initial_line)][initial_direction]
        dates = timejoin.get_dates(
            route_line_mapping[str(initial_line)],
            initial_stop.split("-", 1)[0],
            int(initial_direction),
        )
    elif "d-dropdown" == ctx.triggered_id:
        dates = timejoin.get_dates(
            route_line_mapping[str(initial_line)],
            initial_stop.split("-", 1)[0],
            int(initial_direction),
        )
        stops = line_stop_mapping["all_lines"][str(initial_line)][initial_direction]
    return lines, stops, dates, stop_value, date_value


@app.callback(
    Output("container", "children"),
    [
        Input("add-graph", "n_clicks"),
        Input("add-graph-head", "n_clicks"),
        Input("add-table", "n_clicks"),
        Input("add-map", "n_clicks"),
    ],
    [
        State("container", "children"),
        State("date-dropdown", "value"),
        State("s-dropdown", "value"),
        State("d-dropdown", "value"),
        State("l-dropdown", "value"),
        State("t-dropdown", "value"),
    ],
    manager=long_callback_manager,
)
def display_graphs(
    n_clicks,
    n_clicks_head,
    n_clicks_table,
    n_clicks_map,
    div_children,
    initial_date,
    initial_stop,
    initial_direction,
    line,
    mode,
):
    new_child = None
    stop_id, stop_name = initial_stop.split("-", 1)
    direction = int(initial_direction)
    date = initial_date
    print(stop_id, stop_name, direction, date)
    if "add-graph" == ctx.triggered_id or "add-graph-head" == ctx.triggered_id:
        fig = None
        if "add-graph" == ctx.triggered_id:
            fig = timejoin.map_gtfs(
                route_id=route_line_mapping[str(line)],
                stop_id=stop_id,
                direction=direction,
                cd_date=date,
                content="delay",
            )
        else:
            fig = timejoin.map_gtfs(
                route_id=route_line_mapping[str(line)],
                stop_id=stop_id,
                direction=direction,
                cd_date=date,
                content="headway",
            )
        new_child = html.Div(
            style={
                "width": "100%",
                "display": "inline-block",
                "outline": "thin lightgrey solid",
                "height": "40%",
            },
            draggable="true",
            children=[
                dcc.Graph(id={"type": "dynamic-graph", "index": n_clicks}, figure=fig),
                # dcc.RadioItems(
                #     id={"type": "dynamic-choice", "index": n_clicks},
                #     options=[
                #         {"label": "Inter Arrival Time", "value": "time"},
                #         {"label": "Delay", "value": "delay"},
                #     ],
                #     value="delay",
                # ),
                # dcc.Dropdown(
                #     id={"type": "dynamic-dpn-s", "index": n_clicks},
                #     options=[
                #         {"label": s, "value": s} for s in np.sort(df["state"].unique())
                #     ],
                #     multi=True,
                #     value=["Andhra Pradesh", "Maharashtra"],
                # ),
                # dcc.Dropdown(
                #     id={"type": "dynamic-dpn-ctg", "index": n_clicks},
                #     options=[
                #         {"label": c, "value": c} for c in ["caste", "gender", "state"]
                #     ],
                #     value="state",
                #     clearable=False,
                # ),
                # dcc.Dropdown(
                #     id={"type": "dynamic-dpn-num", "index": n_clicks},
                #     options=[
                #         {"label": n, "value": n}
                #         for n in ["detenues", "under trial", "convicts", "others"]
                #     ],
                #     value="convicts",
                #     clearable=False,
                # ),
            ],
        )
    elif "add-table" == ctx.triggered_id:
        df = timejoin.map_gtfs(
            route_id=route_line_mapping[str(line)],
            stop_id=stop_id,
            direction=direction,
            cd_date=date,
            content="table",
        )
        # print(df.dtypes)
        df = df[
            [
                "route_id",
                "trip_headsign",
                "stop_sequence",
                "processed_arrival_datetime",
                "mapped_time",
                "delay_in_min",
                "inter_arrival_time",
            ]
        ]
        new_child = html.Div(
            style={},
            children=[
                dash_table.DataTable(
                    id={"type": "mapped-table", "index": n_clicks},
                    columns=[
                        {"name": i, "id": i, "deletable": True, "selectable": True}
                        for i in df.columns
                    ],
                    style_header={
                        "backgroundColor": "rgb(30, 30, 30)",
                        "color": "white",
                    },
                    style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
                    style_data_conditional=[
                        {
                            "if": {
                                "filter_query": "{delay_in_secs} > 60",
                                "column_id": "delay_in_secs",
                            },
                            "color": "tomato",
                            "fontWeight": "bold",
                        },
                        # {
                        #     'if': {
                        #         'filter_query': '{Pressure} > 19',
                        #         'column_id': 'Pressure'
                        #     },
                        #     'textDecoration': 'underline'
                        # }
                    ],
                    data=df.to_dict("records"),
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                )
            ],
        )
    elif "add-map" == ctx.triggered_id:
        file_name = map_maker(mode,line,int(initial_direction),initial_stop)
        new_child = html.Div(
            style={},
            children=[
                html.Iframe(
                    className ="second-row",
                    id={"type": "mapped-map", "index": n_clicks},
                    srcDoc=open(f"{file_name}", "r").read(),
                )
            ],
        )
    div_children.append(new_child)
    return div_children


# @app.long_callback(
#     Output("container", "children"),
#     [Input("add-table", "n_clicks"),
#             Input('s-dropdown', 'value'),
#               Input('l-dropdown', 'value'),
#               Input('d-dropdown', 'value')],
#     [State("container", "children")],
# )
# def display_table(n_clicks,stop,line,direction,div_children):
#     print(stop,line,direction)
#     df =  timejoin.map_gtfs(stop_id=8071,stop_name="MERODE", direction=1, send_dataframe=True)
#     new_child = html.Div(
#         children= [dash_table.DataTable(
#         id={"type": "mapped-table", "index": n_clicks},
#         columns=[
#             {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
#         ],
#         data=df.to_dict('records'),
#         editable=True,
#         filter_action="native",
#         sort_action="native",
#         sort_mode="multi",
#         column_selectable="single",
#         row_selectable="multi",
#         row_deletable=True,
#         selected_columns=[],
#         selected_rows=[],
#         page_action="native",
#         page_current= 0,
#         page_size= 10,
#     )])
#     div_children.append(new_child)
#     return div_children


# @app.long_callback(
#     Output({"type": "dynamic-graph", "index": MATCH}, "figure"),
#     [
#         # Input(
#         #     component_id={"type": "dynamic-dpn-s", "index": MATCH},
#         #     component_property="value",
#         # ),
#         # Input(
#         #     component_id={"type": "dynamic-dpn-ctg", "index": MATCH},
#         #     component_property="value",
#         # ),
#         # Input(
#         #     component_id={"type": "dynamic-dpn-num", "index": MATCH},
#         #     component_property="value",
#         # ),
#         Input({"type": "dynamic-choice", "index": MATCH}, "value"),
#     ],
#     manager=long_callback_manager,
# )
# def update_graph(
#     # s_value, ctg_value, num_value,
#  chart_choice):
#     # fig = timejoin.map_gtfs(stop_id=8071,stop_name="MERODE", direction=1)
#     return fig
# dff = df[df["state"].isin(s_value)]

# if chart_choice == "bar":
#     dff = dff.groupby([ctg_value], as_index=False)[
#         ["detenues", "under trial", "convicts", "others"]
#     ].sum()
#     fig = px.bar(dff, x=ctg_value, y=num_value)
#     return fig
# elif chart_choice == "line":
#     if len(s_value) == 0:
#         return {}
#     else:
#         dff = dff.groupby([ctg_value, "year"], as_index=False)[
#             ["detenues", "under trial", "convicts", "others"]
#         ].sum()
#         fig = px.line(dff, x="year", y=num_value, color=ctg_value)
#         return fig
# elif chart_choice == "pie":
#     fig = px.pie(dff, names=ctg_value, values=num_value)

#     return fig


if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(port=8051, host="0.0.0.0")
