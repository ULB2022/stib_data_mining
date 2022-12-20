"""User interface code"""
import dash  # version 1.13.1
import dash_bootstrap_components as dbc
import diskcache
# import dash as html
# import dash as dcc
from dash import ctx, dash_table, dcc, html
from dash.dcc import Dropdown
from dash.dependencies import  Input, Output, State
from dash.html import Div, Label
from dash.long_callback import DiskcacheLongCallbackManager
from map import map_maker
from options import line_stop_mapping, mode_line_mapping, route_line_mapping

import timejoin

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = dash.Dash(
    __name__, title="STIB ANALYTICS", external_stylesheets=[dbc.themes.LUMEN]
)
app._favicon = "MIVB_STIB_Logo.svg.png"


markdown = dcc.Markdown(
    """
<div align="center">  <H1> Bonjour,Je suis STIB ANALYTICS ! </H1> </div>

Hi! I am an Interactive dashboard for STIB! I can be used in many ways. You can check my features in [How to use me](#how-to-use-me) Section. You can find my code [here](https://github.com/ULB2022/stib_data_mining). I am created to help you. To meet me creators, please check [Developers](#developers) Section.  Hope you like me.😊 
<br>

<p align="center">
  <img src="./assets/train.gif" width="500" height="200"/>
</p>


<br>

# How to Use Me
I have multiple options to choose from and multiple to click on.
### Options to Choose
1. **Select Transport:** Choose which transport you want to analyze. I have three options `Metro`, `Bus` and `Tram`. By default `Tram` is chosen.
2. **Select Line:** Choose which line which need to be analyzed. It will keep changing for each Transport.
3. **Select Direction:** `0` and `1` are two directions which can be selected for to and fro direction.
4. **Select Stop:** It will be populated after selection of `Transport`, `Line` and `Direction`. It will have `Stop Id` and `Stop Name`.
5. **Select Date:** It will be populated after selection of  `Transport`, `Line` , `Direction` and `Stop`. It will provide the options for all the data available.

### Buttons to Click
1. **ADD DELAY GRAPH:** After selection of all the above options. It can be clicked and It will show the `bar` graph in which x axis will be the time at which vehicle need to be on stop and after how much time it really come arrived. On this graph line punctuality and regularity is also shown.
2. **ADD HEADWAY GRAPH:** After selection of all the options it will show the scheduled the bar graph between the `scheduled arrival time` and `Inter arrival time`.  Inter arrival time is having 2 parts. First is 
<div style="color:green;display:inline">scheduled</div> and <div style="color:red;display:inline">real</div> interval time. On this graph line punctuality and regularity is also shown.
3. **ADD TABLE:** It will show the tabular format of data which can be useful to see processed arrival time, delays and stop sequence. It will be beneficial to compare 2 stops together.
4. **ADD MAP:** Only   `Transport`, `Line` and `Direction` need to be chosen for this. It can be used to see the stops and direction in which vehicle need to move. It gives bird view about the line.
5. **WAITING TIME:** ***All*** the options need to be chosen. It will show `Schudled waiting time`, `Actual waiting time` and `Excess waiting time`.
6. **DAY ISSUES:** ***All*** the options need to be chosen. It will show all the issue happened on the on that day in map.
7. **CLEAR DASHBOARD:** Click on it to clear all the graphs and maps from the dashboard.

   >  ***All tables are filterable and can be sorted according to it's values.***



## DEVELOPERS


| Adina        | Koumudi           | Prashant  | Rishika  |
| :-------------: |:-------------:|: -----:|:-----:|
| <img src="./assets/adina.jpg" width="200" height="200" />      | <img src="./assets/koumudi.jpg" width="200" height="200" /> | <img src="./assets/prashant.jpg" width="200" height="200" /> |<img src="./assets/rishika.jpg" width="200" height="200" />|


""",
    dangerously_allow_html=True,
    link_target="_blank",
)
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
                dbc.Tooltip(
                    "Select Transport," "Line, Direction, Stop and date",
                    target="add-graph",
                ),
                html.Button(
                    "Add Headway Graph",
                    id="add-graph-head",
                    n_clicks=0,
                    className="btn btn-primary",
                ),
                dbc.Tooltip(
                    "Select Transport, " "Line, Direction, Stop and Date",
                    target="add-graph-head",
                ),
                html.Button(
                    "Add Table", id="add-table", n_clicks=0, className="btn btn-light"
                ),
                dbc.Tooltip(
                    "Select Transport," "Line, Direction, Stop and date",
                    target="add-table",
                ),
                html.Button(
                    "Add Map", id="add-map", n_clicks=0, className="btn btn-success"
                ),
                dbc.Tooltip(
                    "Select Transport," "Line, Direction",
                    target="add-map",
                ),
                html.Button(
                    "WAITNG TIME", id="add-ewt", n_clicks=0, className="btn btn-success"
                ),
                dbc.Tooltip(
                    "Select Transport," "Line, Direction, Stop and date",
                    target="add-ewt",
                ),
                html.Button(
                    "DAY ISSUES",
                    id="add-issues",
                    n_clicks=0,
                    className="btn btn-danger",
                ),
                dbc.Tooltip(
                    "Check day wise issue.Please select Transport,"
                    "Line, Direction, Stop and date",
                    target="add-issues",
                ),
                html.Button(
                    "Clear Dashboard",
                    id="clear-dashboard",
                    n_clicks=0,
                    className="btn btn-danger",
                ),
                dbc.Tooltip(
                    "Clear the dashboard",
                    target="clear-dashboard",
                ),
            ],
            style={"text-align": "center"},
        ),
        html.Div(id="container", children=[markdown], className="wrapper"),
    ]
)


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
    print()
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
        Input("add-ewt", "n_clicks"),
        Input("add-issues", "n_clicks"),
        Input("clear-dashboard", "n_clicks"),
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
    n_clicks_ewt,
    n_clicks_issues,
    n_clicks_clear,
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
                html.H3(
                    f"Delay for {route_line_mapping[str(line)]} {stop_id} {stop_name} for direction {direction}"
                ),
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
                ),
            ],
        )
    elif "add-ewt" == ctx.triggered_id:
        df = timejoin.map_gtfs(
            route_id=route_line_mapping[str(line)],
            stop_id=stop_id,
            direction=direction,
            cd_date=date,
            content="ewt",
        )
        df = df[
            [
                "cluster",
                "start_time",
                "end_time",
                "regularity",
                "swt",
                "awt",
                "ewt",
            ]
        ]
        df = df.rename(
            columns={
                "swt": "Scheduled Waiting Time",
                "awt": "Actual Waiting Time",
                "ewt": "Estimated Waiting Time",
                "regularity": "Regularity/Puncuality",
            }
        )

        df = df.round(2)
        new_child = html.Div(
            style={},
            children=[
                html.H3(
                    f"Estimasted Waiting Time for {route_line_mapping[str(line)]} {stop_id} {stop_name} for direction {direction}"
                ),
                dash_table.DataTable(
                    id={"type": "mapped-ewt", "index": n_clicks},
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
                                "filter_query": "{regularity} ==1",
                                "column_id": "regularity",
                            },
                            "color": "green",
                            "fontWeight": "bold",
                        },
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
                ),
            ],
        )
    elif "add-map" == ctx.triggered_id:
        file_name = map_maker(mode, line, int(initial_direction), initial_stop)
        new_child = html.Div(
            style={},
            children=[
                html.H3(f"Map for route {route_line_mapping[str(line)]}"),
                html.Iframe(
                    className="second-row",
                    id={"type": "mapped-map", "index": n_clicks},
                    srcDoc=open(f"{file_name}", "r").read(),
                ),
            ],
        )
    elif "add-issues" == ctx.triggered_id:
        # try:
        new_child = html.Div(
            style={},
            children=[
                html.H3(f"Issues for Date {date}"),
                html.Iframe(
                    className="second-row",
                    id={"type": "mapped-issue", "index": n_clicks},
                    srcDoc=open(
                        f"data/issue_map_{date.replace('-','_')}.html", "r"
                    ).read(),
                ),
            ],
        )
    elif "clear-dashboard" == ctx.triggered_id:
        div_children = []
        new_child = markdown
    if ctx.triggered_id != None and "clear-dashboard" != ctx.triggered_id:
        print(div_children[0]["type"] == "Markdown")
        if div_children[0]["type"] == "Markdown":
            div_children.pop()
    if new_child != None:
        div_children.insert(0, new_child)
    return div_children


if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(port=8051, host="0.0.0.0")
