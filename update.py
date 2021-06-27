#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 15:37:11 2021.

@author: chrissy
"""
import random

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

import toml
import pandas as pd
import dash_table

from loguru import logger
from gethostdata import hostdata

from LogToFile import LogManager

from datetime import datetime

from database_actions import databaseActions as db
from models import engine

SQLALCHEMY_TABLE_NAME: str = "host_status_table"

# external_stylesheets: list = ["/assets/reset.css"]
# external_stylesheets: list = [
#    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
# ]

colors = {"background": "rgb(50, 50, 50)", "text": "#FFFFFF"}

# logger.info(type(external_stylesheets))


app = dash.Dash(__name__, title="Host monitor")
# , external_stylesheets=external_stylesheets)
app.layout = html.Div(html.H4("Heading", style={"backgroundColor": "blue"}))
# app = dash.Dash(__name__)

w: hostdata = hostdata()

if not db.DoesTableExist():
    logger.info("tablestatus: " + "Table Does Not Exist")
    df = w.queryhosts(app, dict)
else:
    logger.info("tablestatus: " + "Table Exists")

# Get the number of records in the toml file
"""
db.sync_config_to_db(
    app,
)
"""
hostconfig: dict = toml.load("app.config.toml")
# logger.info(hostconfig)


# configdict: dict = toml.load("app.config.toml")
# app.logger.info(dict)

app.layout = html.Div(
    html.Div(
        [
            html.H4("Host status check", style={"textAlign": "left"}),
            html.Div(id="live-update-text"),
            dash_table.DataTable(
                id="host-table",
                columns=[
                    {
                        "name": "DateAndTime",
                        "id": "DateAndTime",
                        "editable": False,
                    },
                    {
                        "name": "descriptive_name",
                        "id": "descriptive_name",
                        "editable": False,
                    },
                    {"name": "host", "id": "host", "editable": False},
                    {"name": "Status", "id": "Status", "editable": False},
                    {"name": "Test", "id": "Test", "editable": False},
                    {"name": "Reason", "id": "Reason", "editable": False},
                    {"name": "last Moved To down", "id": "last_down", "editable": False},
                    {"name": "Last Moved To Up", "id": "last_up", "editable": False},
                ],
                # Read data from the dictionary that has been craeted from the
                # current sql table.
                data=db.readtable(),
                # Set cell color dependant or marked UP or DOWN
                style_data_conditional=[
                    {
                        "if": {
                            "filter_query": '{Status} ="UP"',
                            "column_id": "Status",
                        },
                        "color": "LawnGreen",
                    },
                    {
                        "if": {
                            "filter_query": '{Status} !="UP"',
                            "column_id": "Status",
                        },
                        "backgroundColor": "tomato",
                        "color": "white",
                    },
                ],
                style_header={"backgroundColor": "rgb(30, 30, 30)"},
                style_cell={
                    "backgroundColor": "rgb(50, 50, 50)",
                    "color": "white",
                    "font_size": "14px",
                    "text_align": "left",
                },
                fill_width=False,
                editable=True,
            ),
            html.Div(
                html.H5(
                    id="table-action-outputs",
                    children="",
                    style={"textAlign": "left"},
                ),
                style={
                    "width": "100%",
                    " display": "inline-block",
                    "float": "left",
                    "color": colors["text"],
                    "backgroundColor": colors["background"],
                },
            ),
            html.Div(
                html.H3("hh1", id="showit", style={"textAlign": "left"}),
                style={
                    "width": "100%",
                    " display": "inline-block",
                    "float": "left",
                    "backgroundColor": colors["background"],
                    "color": colors["text"],
                },
            ),
            html.Div(
                [
                    dcc.Textarea(
                        className="custom-tabs-container",
                        id="textarea-example",
                        value="Textarea content initialized\nwith multiple lines of text",
                        style={
                            "width": "100%",
                            "height": 300,
                            "backgroundColor": colors["background"],
                            "color": colors["text"],
                        },
                    ),
                    html.Div(
                        id="textarea-example-output",
                        className="custom-tabs-container",
                    ),
                ]
            ),
            # dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id="interval-component",
                interval=60 * 1000,  # in milliseconds
                n_intervals=0,
            ),
        ]
    ),
)


@app.callback(
    dash.dependencies.Output("host-table", "data"),
    dash.dependencies.Output("showit", "children"),
    [dash.dependencies.Input("interval-component", "n_intervals")],
)
def updatetable(n):
    """
    Updates the display from the latest view of the sql table.
    
    Returns
    -------
    A dictionary from the sql table.
    """
    hostconfig: dict = toml.load("app.config.toml")
    df_new = w.queryhosts(app, hostconfig)
    z: str = db.insertValue(
        app, df_new
    )  # returns 'Field Updated or Row Created'
    sql_table_df = pd.read_sql_table(
        "host_status_table",
        engine,
        columns=[
            "DateAndTime",
            "descriptive_name",
            "host",
            "Status",
            "Test",
            "Reason",
            "last_down",
            "last_up",
        ],
    )

    data: dict = sql_table_df.to_dict("records")
    now: datetime = datetime.now()
    dt_string: str = now.strftime("%d/%m/%Y %H:%M:%S")
    message = z + " " + dt_string
    # logger.info(data)
    return data, message


'''
@app.callback(
    dash.dependencies.Output("showit", "children"),
    [dash.dependencies.Input("interval-component", "n_intervals")],
)
def updaterand(n):
    """
    Return a random number, just for testing.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """
    randoms = str(random.randint(3, 105))
    # logger.info("random !!!!!")
    return randoms
'''


@app.callback(
    Output("textarea-example", "value"),
    [dash.dependencies.Input("interval-component", "n_intervals")],
)
def update_output(value):
    """
    Display the log file for any host changes.
    
    Returns
    -------
    A reversed list of entries, so lates updatea are at the top.

    """
    with LogManager("logfile.txt", "r") as f:
        lines = f.readlines()
    lines = reversed(lines)
    value = "".join(map(str, lines))
    return value


if __name__ == "__main__":
    app.logger.setLevel = lambda x: None
    # logging.basicConfig(level=logging.DEBUG)
    app.enable_dev_tools(
        dev_tools_ui=True,
        dev_tools_serve_dev_bundles=True,
    )
    app.run_server(debug=True, dev_tools_ui=True, dev_tools_props_check=False)
