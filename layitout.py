import dash
from dash import dcc
from dash import html
from layout_dbc import layitout_sync
from layout_dbc import layitout_host_status
from layout_dbc import layitout_arp_status
from layout_dbc import layitout_arp
from layout_dbc import layitout_hosts
from callbacks import get_callbacks

from flask_loguru import logger

from waitress import serve

import sys

# import dash_table_experiments as dt
import dash_bootstrap_components as dbc
from layout_dbc import layitout_arp
from layout_dbc import layitout_hosts
from layout_dbc import layitout_logs


app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG],)
#app.logger.handlers.pop()
'''
logger.debug(app.logger.handlers)
for handler in app.logger.handlers:
    logger.info("count")
    app.logger.removeHandler(handler)

logger.debug("out")


if (app.logger.hasHandlers()):
    logger.info("handle")
    app.logger.handlers.clear()


if (app.logger.hasHandlers()):
    app.logger.info("no handle")
    app.logger.handlers.clear()

if (app.logger.hasHandlers()):
    app.logger.info("no handle 1")
    app.logger.handlers.clear()

if (app.logger.hasHandlers()):
    app.logger.info("no handle 2")
    app.logger.handlers.clear()
'''

logger.add("file.log")
logger.add(sys.stderr)


app.layout = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            layitout_host_status, style={'width': '100%'}
                        )
                    ],
                    width=4,
                ),
                dbc.Col(
                    [dbc.Button(layitout_arp_status, style={'width': '100%'})],
                    width=4,
                ),
                dbc.Col(
                    [dbc.Button(layitout_sync, style={'width': '100%'})],
                    width=4,
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [dbc.Button(layitout_hosts, style={'width': '100%'})],
                    width=6,
                ),
                dbc.Col(
                    [dbc.Button(layitout_arp, style={'width': '100%'})],
                    width=6,
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [dbc.Button(layitout_logs, style={'width': '100%'})],
                    width=5,
                ),
                dbc.Col(
                    [dbc.Button('row 3 col 2', style={'width': '100%'})],
                    width=5,
                ),
            ]
        ),
    ],
    fluid=True,
)


app.logger.critical("Critical Hello world")

logger.error("Fail Hello world")

logger.warning("Warning Hello world")

logger.info("Info Hello world")

logger.debug("Debug Hello world")
app.logger.info('message')

get_callbacks(app)

if __name__ == '__main__':
    # app.run_server(debug=True, port=8050, host='0.0.0.0')
    serve(app.server, host="127.0.0.1", port=8050, threads=8)

    # app.logger.setLevel = "DEBUG"
    '''
    app.run_server(
        debug=True,
        dev_tools_ui=True,
        dev_tools_serve_dev_bundles=True,
        dev_tools_props_check=False,
        port=8050,
        threaded=True,
        host='0.0.0.0',
    )
    '''

