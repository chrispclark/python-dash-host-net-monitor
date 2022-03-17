"""
Open_db.py database access.

Define the sqlite database and create classes to work with the data
"""
from datetime import datetime
from sqlalchemy import inspect

# from sqlalchemy.orm import sessionmaker, configure_mappers, declarative_base
# from loguru import logger
from flask_loguru import logger
from typing import List, Tuple, Any
from plyer import notification
import ipaddress

# from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import toml
import arpreq
from models import (
    host_status_table,
    arp_status_table,
    SQLModelDBConnection,
    engine,
)

# from colors import red, green, blue
# from general_functions import LogAndNotify
from general_functions import GeneralFunctions

pd.set_option('display.max_rows', 500)

RED = '\u001b[31;1m'
GREEN = '\u001b[32;1m'
BLUE = '\u001b[34;1m'
RESET = '\u001b[0m'
MAGENTA = '\u001b[35;1m'

SQLALCHEMY_DATABASE_URI: str = 'sqlite:///hoststatus.db'
SQLALCHEMY_TABLE_NAME = 'host_status_table'
TABLE_NAME = host_status_table


class DatabaseActions:
    """
    Form a complex number.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """

    TABLE_NAME = host_status_table
    logger.debug("db actions")

    @staticmethod
    def getfailedarp(conn_str):
        """
        list all database entries marked as ARP but currently not responding.

        Returns.
        -------
        List of IP addresses that are in the sql table but not currently
        responding to discovery.
        """
        iplistnoarp = []
        aquery = []
        with SQLModelDBConnection(conn_str) as db_connection:
            aquery: list = (
                db_connection.session.query(arp_status_table)
                .filter_by(type='discovery')
                .all()
            )
        for row in aquery:
            ip_address = row.descriptive_name
            last_down = row.last_down
            last_up = row.last_up
            try:
                if arpreq.arpreq(ip_address) is None:
                    new_list = [ip_address, last_down, last_up]
                    iplistnoarp.append(new_list)
            except ValueError:
                logger.info('address/netmask is invalid for IPv4:', ip_address)
            # return a list of lists that contains the non responding IP addresses
        return iplistnoarp

    @staticmethod
    def does_table_exist() -> bool:
        """
        Summary.
        --------
        Check if the table exists using sqlalchemy inspection

        Returns:
        --------
        False if it does not exist
        True if it does exist
        """
        ins = inspect(engine)
        ret: bool = ins.dialect.has_table(
            engine.connect(), SQLALCHEMY_TABLE_NAME
        )
        return ret

    @classmethod
    def list_table_fields(cls, table_name):
        # logger.info(type(table_name))
        z = table_name.__table__.columns.keys()
        z.remove('id') if 'id' in z else None  # Does nothing if '' not in s
        # logger.info(z)
        return z

    @classmethod
    def does_value_exist(cls, conn_str, search):
        with SQLModelDBConnection(conn_str) as db_connection:
            aquery: int = (
                db_connection.session.query(TABLE_NAME)
                .filter_by(descriptive_name=search)
                .count()
            )
        return aquery

    @classmethod
    def insert_row(cls, conn_str, row_data: dict) -> str:
        with SQLModelDBConnection(conn_str) as db_connection:
            db_connection.session.add(TABLE_NAME(**row_data))
        return 'added row'

    @staticmethod
    def readtable(table_name) -> list:
        """
        Summary:
        --------
        Fill a dataframe with data from the sql table and convert to dict

        Returns:
        --------
        A list of dictionary of records inside a single list
        """
        sql_table_df = pd.read_sql_table(
            table_name,
            engine,
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
        # logger.info(type(sql_table_df))

        sql_table_df.sort_values(
            by='descriptive_name',
            inplace=True,
            key=lambda col: col.str.lower(),
        )
        # Convert table to multiple dict inside a single list
        # logger.info(sql_table_df.to_dict(orient='records'))
        data: list = sql_table_df.to_dict('records')
        return data

    @staticmethod
    def sync_config_to_db(conn_str, TABLE_NAME) -> int:
        """
        Summary:
        --------
        Make sure all entries in the toml config file exist in the database.

        Parameters
        ----------

        Returns
        -------
        The count of matching records.
        """
        hostconfig: (tuple[str, Any],) = toml.load('app.config.toml')
        # logger.info(hostconfig)
        for key in hostconfig:
            hostconfig_dict: dict = hostconfig[key]
            # logger.info(hostconfig_dict)
            aquery = 0
            with SQLModelDBConnection(conn_str) as db_connection:
                aquery: int = (
                    db_connection.session.query(TABLE_NAME)
                    .filter_by(descriptive_name=key)
                    .count()
                )
                # Check for any new entries in the TOML config file and add to the host table.
                # Ignore any network ranges for discovery as they will always show done and are handled by
                # the getarpdata.py module
            if aquery == 0 and hostconfig_dict['type'] != 'discovery':
                logger.info(RED + 'Search Failed, creating: ' + key + RESET)
                logger.info(hostconfig_dict)
                dt_string: str = GeneralFunctions.datetimestring()
                c = TABLE_NAME(
                    mask=hostconfig_dict['mask'],
                    DateAndTime=dt_string,
                    descriptive_name=key,
                    host=hostconfig_dict['host'],
                    check=hostconfig_dict['check'],
                    type=hostconfig_dict['type'],
                    last_up=dt_string,
                    last_down=dt_string,
                    Reason='reason1',
                    Test='test',
                    Status='DOWN',
                )
                logger.info(c)
                with SQLModelDBConnection(conn_str) as db_connection:
                    db_connection.session.add(c)
            else:
                pass
                # logger.info(GREEN + "Search Found, Not creating: " + key + RESET)
        return aquery

    @staticmethod
    def insert_value(
        conn_str: object, TABLE_NAME: object, df_latest_update: object
    ) -> str:
        """
        Summary.

        Parameters
        ----------
        conn_str : TYPE
        TABLE_NAME:
        df_latest_update:

        DESCRIPTION.

        Returns
        -------
        None.
        """
        dt_string: str = GeneralFunctions.datetimestring()
        # Save a copy of the latest update to .csv file
        df_latest_update.to_csv('df_latest_update.csv')

        # get the count of rows in sql table
        with SQLModelDBConnection(conn_str) as db_connection:
            table_count: int = db_connection.session.query(TABLE_NAME).count()

        # Get the current table into a dataframe and convert into a dictionary
        # before we update anything, so we can compare with the live feed to
        # see if anything has changed
        previous_status_df: pd.DataFrame = pd.read_sql_table(
            TABLE_NAME.__name__,
            engine,
            columns=['descriptive_name', 'Status', 'host'],
        )
        previous_status_df.set_index('descriptive_name', inplace=True)
        previous_status_dict = previous_status_df.to_dict()

        # Iterate though each item in the latest dataframe so we can:
        # See if there are any new entries that we will have to add to the
        # sql table. This will be the descriptive name
        # Mark any changes between the latest dataframe and what is
        # currently stored in the sql table. This will be the status
        # (up or down)
        for item in range(0, df_latest_update.shape[0]):
            # shape [0] gives the number of rows.
            # shape [1] gives the number of columns.
            series = df_latest_update.T[item]
            latest_update_dict: dict = series.to_dict() # A dictionary of each pandas row
            # logger.info(latest_update_dict)
            search: str = latest_update_dict['descriptive_name']
            # logger.info(search)
            hostname = ''

            '''Check if search is an IP address and return 'hostname', [], [IPAddress])
            Otherwise return (None, None, None)
            '''
            check_ip = GeneralFunctions.validate_ip_address(search)
            # logger.info(check_ip)
            if all(elem is None for elem in check_ip):
                hostname = ''
            else:
                hostname = check_ip[0]

            host_status: str = latest_update_dict['Status']
            host: str = latest_update_dict['host']
            reason: str = latest_update_dict['Reason']
            lastup: str = latest_update_dict['last_up']
            lastdown: str = latest_update_dict['last_down']
            # logger.info(latest_update_dict)
            # Get a count of how many entries in the sql table match by
            # descriptive name, so we can add any new entries or any updated
            # entries

            '''Check if descriptive name already exists in the table
            '''
            with SQLModelDBConnection(conn_str) as db_connection:
                aquery: int = (
                    db_connection.session.query(TABLE_NAME)
                    .filter_by(descriptive_name=search)
                    .count()
                )
            if (
                aquery == 0
            ):
                logger.info(RED + 'Search Failed, creating: ' + search + RESET)
                with SQLModelDBConnection(conn_str) as db_connection:
                    db_connection.session.add(TABLE_NAME(**latest_update_dict))
            # logger.info(GREEN + "Search: " + d + RESET)
            '''Now let us check the host_status field to see if anything has changed
            between the latest dataframe and what is in the sql table.
            '''
            try:
                previous_status: str = previous_status_dict['Status'][search]
            except KeyError:
                logger.error(
                    'Key is missing, let use rebuild, maybe the table was deleted'
                )

            # logger.info(BLUE + previous_status + RESET)
            # logger.info(host_status)
            with SQLModelDBConnection(conn_str) as db_connection:
                aquery = (
                    db_connection.session.query(TABLE_NAME)
                    .filter_by(descriptive_name=search)
                    .one()
                )
            if previous_status != host_status:
                if previous_status == 'UP':
                    logger.info(
                        RED + search + ' ' + 'Moved from UP to DOWN' + RESET
                    )
                    with SQLModelDBConnection(conn_str) as db_connection:
                        db_connection.session.query(TABLE_NAME).filter_by(
                            descriptive_name=search
                        ).update(
                            {
                                'last_down': dt_string,
                                'Status': 'DOWN',
                                'DateAndTime': dt_string,
                            },
                            synchronize_session='fetch',
                        )
                    logdata = (
                        dt_string
                        + ' Moved to down: '
                        + search
                        + ' '
                        + hostname
                    )
                    GeneralFunctions.writeIt('logfile.txt', 'a', logdata)
                elif previous_status != 'UP':
                    logger.info(
                        GREEN + search + ' ' + 'Moved from DOWN to UP' + RESET
                    )
                    with SQLModelDBConnection(conn_str) as db_connection:
                        db_connection.session.query(TABLE_NAME).filter_by(
                            descriptive_name=search
                        ).update(
                            {
                                'last_up': dt_string,
                                'Status': 'UP',
                                'DateAndTime': dt_string,
                            },
                            synchronize_session='fetch',
                        )
                    logdata = (
                        dt_string + ' Moved to up: ' + search + ' ' + hostname
                    )
                    GeneralFunctions.writeIt('logfile.txt', 'a', logdata)
                    """
                    with LogManager('logfile.txt', 'a') as log_file:
                        log_file.write(dt_string + ' Moved to up: ' + search)
                        log_file.write('\n')
                        GeneralFunctions.send_notification('ALERT', ' Moved to up: ' + search
                    """
                elif not previous_status:
                    logger.error('Not UP or DOWN, so let us rebuild the table')
                    with SQLModelDBConnection(conn_str) as db_connection:
                        db_connection.session.query(TABLE_NAME).filter_by(
                            descriptive_name=search
                        ).update(
                            {'last_up': dt_string},
                            synchronize_session='fetch',
                        )

                    logdata = (
                        dt_string
                        + ' Moved from undefined :   '
                        + search
                        + ' hostname'
                    )
                    GeneralFunctions.writeIt('logfile.txt', 'a', logdata)
                    """    
                    with LogManager('logfile.txt', 'a') as log_file:
                        log_file.write(dt_string + ' Moved from undefined :   ' + search)
                        log_file.write('\n')
                        GeneralFunctions.send_notification('ALERT', ' Moved from undefined: ' + search)
                    """
                else:
                    logdata = (
                        dt_string
                        + ' What the heck not UP or DOWN: '
                        + search
                        + ' '
                        + hostname
                        + previous_status
                        + ' '
                        + host_status
                    )
                    GeneralFunctions.writeIt('logfile.txt', 'a', logdata)
                    """
                    with LogManager('logfile.txt', 'a') as log_file:
                        log_file.write(
                            dt_string
                            + ' What the heck not UP or DOWN: '
                            + search
                            + ' '
                            + previous_status
                            + ' '
                            + host_status
                        )
                        log_file.write('\n')
                        GeneralFunctions.send_notification('ALERT', ' Not Up Or Down ' + search + " " + previous_status + " " + host_status)
                    """

        if table_count == 0:
            return 'Row Created'
        return 'Field Updated'


if __name__ == '__main__':
    """
    Form a complex number.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """

    now: datetime = datetime.now()
    b = DatabaseActions()
    c = b.getfailedarp('sqlite:///hoststatus.db')
    logger.info(c)
    # b.sync_config_to_db()
    # message = pd.read_csv("df_latest_update.csv", index_col=0)
    # c1 = table(DateAndTime = now.strftime("%d/%m/%Y %H:%M:%S"), host_name = 'Station Road Nanded', host_status = 'ravi@gmail.com')
    # session.add(c1)
    # session.commit()
    # z.listmessage(message)
    # b.insert_value(message, message)
    # z.searchValue(session, "jim")
    # result = session.query(table).all()
    # res = session.query(table).all()
    # print(result)
