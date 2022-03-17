#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 18:32:03 2021.

@author: chrissy
"""
import socket
import ipaddress
import pandas as pd
import arpreq
import toml

from flask_loguru import logger
from host_commands import GeneralCommands
from database_actions import DatabaseActions
from general_functions import GeneralFunctions
from database_actions import DatabaseActions as db

# from save_to_database import insertData
from pandas import DataFrame

RED = '\u001b[31;1m'
GREEN = '\u001b[32;1m'
BLUE = '\u001b[34;1m'
RESET = '\u001b[0m'
MAGENTA = '\u001b[35;1m'

class HostData(object):
    """
    Summary.

    Returns
    -------
    None.
    """

    def __init__(self, conn_str, toml_config_dict):
        """
        Summary.

        Returns
        -------
        None.

        """
        self.conn_str = conn_str
        # self.conn_str = DatabaseActions.conn_str
        # self.app = app
        # self.dict = dict
        self.toml_config_dict = toml_config_dict
        self.general_commands = GeneralCommands(self.toml_config_dict)
        # logger.info("HostData init")

    def queryhosts(
        self, conn_str, HOST_TABLE_NAME, toml_config_dict, app
    ) -> list:
        """
        Summary.

        Returns
        -------
        None.
        """
        logger.error("Fail Hello world")
        logger.warning("Warning Hello world")
        logger.info("Info Hello world")
        logger.debug("Debug Hello world")
        lst = []
        z: list = DatabaseActions.list_table_fields(HOST_TABLE_NAME)
        for a in lst:
            zip_iterator = zip(z, a)
            a_dictionary: dict = dict(zip_iterator)
            a_dictionary['last_up'] = GeneralFunctions.datetimestring()
            s = DatabaseActions.does_value_exist(
                conn_str, a_dictionary['descriptive_name']
            )
            if not s:
                d = DatabaseActions.insert_row(conn_str, a_dictionary)
        """ 
            Now let us go through the database and see the live status of each host
        """

        lst.clear()
        for descriptive_name, key in toml_config_dict.items():
            # logger.info(key["type"])
            if key['type'] == 'socket':
                Status = GeneralCommands.hostportcheck(
                    key['host'], key['check']
                )
                test = 'Socket'
                # logger.info("This is a socket" + key["check"])
                lst.append(
                    [
                        GeneralFunctions.datetimestring(),
                        descriptive_name,
                        key['host'],
                        key['mask'],
                        key['check'],
                        key['type'],
                        Status,
                        'Socket connection',
                        key['last_down'],
                        key['last_up'],
                    ]
                )
                if any(elem is None for elem in lst):
                    logger.error('None Found lst')

            if key['type'] == 'dns':
                if 'Failed' not in GeneralCommands.reversedns(
                    key['host'], key['host']
                ):
                    Status = 'UP'
                else:
                    Status = 'DOWN'
                # test = "DNS"
                lst.append(
                    [
                        GeneralFunctions.datetimestring(),
                        descriptive_name,
                        key['host'],
                        key['mask'],
                        'check',
                        key['type'],
                        Status,
                        'Reverse DNS Lookup - ' + Status,
                        key['last_down'],
                        key['last_up'],
                    ]
                )
                if any(elem is None for elem in lst):
                    logger.error('None Found lst')

            if key['type'] == 'url':
                # logger.info(descriptive_name)
                # logger.info(key["host"])
                Status = GeneralCommands.url(key['host'])
                if 'UP' in Status:
                    Reason = '220 OK from site'
                else:
                    Reason = 'Connection Error'
                # logger.info(status)
                test = 'url'
                lst.append(
                    [
                        GeneralFunctions.datetimestring(),
                        descriptive_name,
                        key['host'],
                        key['mask'],
                        key['check'],
                        key['type'],
                        Status,
                        Reason,
                        key['last_down'],
                        key['last_up'],
                    ]
                )
                if any(elem is None for elem in lst):
                    logger.error('None Found lst')

        #  Wrap it all up and send the dataframe back
        # logger.info(lst)
        data_frame: DataFrame = pd.DataFrame(
            lst,
            columns=[
                'DateAndTime',
                'descriptive_name',
                'host',
                'mask',
                'check',
                'type',
                'Status',
                'Reason',
                'last_down',
                'last_up',
            ],
        )
        df_new = data_frame.fillna('DOWN')
        # logger.info(MAGENTA + "----------" + RESET)
        # logger.info(MAGENTA + self.fred + RESET)
        # z = self.db.insertValue(self, lst)
        # th pd.option_context("display.max_rows", None, "display.max_columns", None):

        # Pass all that data to insert_value method in database_actions.py to check
        # the status of each host and commit to the sql table.
        try:
            FieldUpdateState: str = db.insert_value(
                conn_str, HOST_TABLE_NAME, df_new
            )  # returns 'Field Updated or Row Created'
        except KeyError:
            logger.info(
                'key error, has something been added to the TOML config'
            )
            FieldUpdateState: str = db.insert_value(
                conn_str, HOST_TABLE_NAME, df_new
            )  # returns 'Field Updated or Row Created'
        ''' df_new is a dataframe of the latest update
        '''
        return [df_new, FieldUpdateState]


if __name__ == '__main__':
    conn_str = 'sqlite:///hoststatus.db'
    table_name = 'host_status_table'
    toml_config = toml.load('app.config.toml')
    b = HostData(conn_str=conn_str, toml_config_dict=toml_config)
    b.queryhosts(
        conn_str=conn_str, table_name=table_name, toml_config_dict=toml_config
    )
