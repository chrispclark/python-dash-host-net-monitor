import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output
from dash import dash_table
import toml
from database_actions import DatabaseActions as db
from models import host_status_table, arp_status_table
from gethostdata import HostData
from getarpdata import DiscoveredHostData
from flask_loguru import logger
from LogToFile import LogManager
from typing import Any
# from layitout import app

hostConfigDict: (tuple[str, Any],) = toml.load('app.config.toml')
conn_str = 'sqlite:///hoststatus.db'
hd = HostData(conn_str, hostConfigDict)
dd = DiscoveredHostData(conn_str, hostConfigDict)

# First check that t


colors = {'background': 'rgb(50, 50, 50)', 'text': '#FFFFFF'}

HOST_TABLE_NAME = host_status_table
ARP_TABLE_NAME = arp_status_table


def get_callbacks(app):
    logger.error("Fail Hello world")
    logger.warning("Warning Hello world")
    logger.info("Info Hello world")
    logger.debug("Debug Hello world")
    # ---------------------   Sync TOML config to SQL Tables -------------------- #
    @app.callback(
        dash.dependencies.Output('button-clicks', 'children'),
        [dash.dependencies.Input('my-button', 'n_clicks')],
    )
    def clicks(n_clicks):
        d = db.sync_config_to_db(conn_str, HOST_TABLE_NAME)
        logger.info(d)
        return 'Button has been clicked {} times'.format(n_clicks)

    # ---------------------   Get ARP status ----------------------------------- #
    @app.callback(
        dash.dependencies.Output('arpstatus_label', 'children'),
        [dash.dependencies.Input('arp-status-update-interval', 'n_intervals')],
    )
    def discover_arp_changes(n):
        """
        Run discovery across the local network.
        Returns
        -------
        A dictionary from the sql table.
        """
        hostConfigDict: (tuple[str, Any],) = toml.load('app.config.toml')

        # Call queryhosts in gethostdata.py for a list of configured host addresses
        # Also discovered arp IP addresses and previously discovered arp IP
        # addresses that are not currently up
        df_new: pd.DataFrame = dd.queryDiscoveredhosts(
            conn_str, hostConfigDict
        )
        with LogManager('arpchanges.txt', 'a') as log_file:
            log_file.write(str(df_new))
            log_file.write('\n')

        # Pass all that data to insert_value method in database_actions.py to check
        # the status of each host and commit to the sql table.
        try:
            table_insert_or_update: str = db.insert_value(
                conn_str, ARP_TABLE_NAME, df_new
            )  # returns 'Field Updated or Row Created'
            logger.info(table_insert_or_update)
        except KeyError:
            logger.info(
                'key error, has something been added to the TOML config'
            )
            all_addresses: str = db.insert_value(
                conn_str, ARP_TABLE_NAME, df_new
            )  # returns 'Field Updated or Row Created'
        # logger.info(table_insert_or_update + " - " + ARP_TABLE_NAME.__name__)
        return 'Discovery Intervals Passed: ' + str(n)

    # ---------------------   Get HOST status ----------------------------------- #
    @app.callback(
        dash.dependencies.Output('hoststatus_label', 'children'),
        [
            dash.dependencies.Input(
                'host-status-update-interval', 'n_intervals'
            )
        ],
    )
    def update_interval(n):
        """
        Updates the table from processed data.

        Returns
        -------
        A dictionary from the sql table.
        """
        hostConfigDict: (tuple[str, Any],) = toml.load('app.config.toml')

        # Call queryhosts in gethostdata.py for a list of configured host addresses
        # Also discovered arp IP addresses and previously discovered arp IP
        # addresses that are not currently up
        connection = hd.queryhosts(conn_str, HOST_TABLE_NAME, hostConfigDict, app)
        # logger.info(df_new)
        # logger.info(type(df_new))

        # logger.info(connection)
        return 'Intervals Passed: ' + str(n)

    # ---------------------   Get ARP data from SQL Table   ---------------------- #
    @app.callback(
        dash.dependencies.Output('arp-table', 'data'),
        [dash.dependencies.Input('arp-table-interval', 'n_intervals')],
    )
    def updatearptable(update_count):
        """
        Updates the display from the latest view of the sql table.

        Returns
        -------
        A dictionary from the sql table.
        """
        data = db.readtable(ARP_TABLE_NAME.__name__)
        # logger.info(data)
        return data

    # --------------------- Get HOST data from SQL Table ---------------------- #
    @app.callback(
        dash.dependencies.Output('host-table', 'data'),
        [dash.dependencies.Input('host-table-interval', 'n_intervals')],
    )
    def updatehosttable(update_count):
        """
        Updates the display from the latest view of the sql table.

        Returns
        -------
        A dictionary from the sql table.
        """
        data: list = db.readtable(HOST_TABLE_NAME.__name__)
        return data

    # --------------------------   Update the log view   ------------------------ #
    @app.callback(
        Output('textarea-example', 'value'),
        Input('log-interval', 'n_intervals'),
    )
    def update_output(value) -> str:
        """
        Display the log file for any host changes.

        Returns
        -------
        A reversed list of entries, so the latest updates are at the top.

        """
        with LogManager('logfile.txt', 'r') as log_file:
            lines = log_file.readlines()
        lines = reversed(lines)
        value = ''.join(map(str, lines))
        return value
