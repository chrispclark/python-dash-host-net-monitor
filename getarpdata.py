import socket
import ipaddress
from typing import List, Tuple, Any

import pandas as pd
import arpreq
import toml
import nmap

from flask_loguru import logger
from host_commands import GeneralCommands
from database_actions import DatabaseActions
from general_functions import GeneralFunctions

# from save_to_database import insertData

RED = '\u001b[31;1m'
GREEN = '\u001b[32;1m'
BLUE = '\u001b[34;1m'
RESET = '\u001b[0m'
MAGENTA = '\u001b[35;1m'

pd.set_option('display.expand_frame_repr', False)


class DiscoveredHostData(object):
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
        self.toml_config_dict = toml_config_dict
        self.general_commands = GeneralCommands(self.toml_config_dict)
        self.nm = nmap.PortScanner()
        self.lst = []
        # logger.info("DiscoveredHostData init")

    def queryDiscoveredhosts(self, conn_str, toml_config_dict) -> pd.DataFrame:
        """
        Summary.

        Returns
        -------
        None.
        """
        # logger.info("queryDiscoveredHosts")
        self.lst.clear()
        # logger.info(toml_config_dict.items())
        for descriptive_name, key in toml_config_dict.items():
            # logger.info(key["type"])
            if key['type'] == 'discovery':
                # logger.info(key["host"])
                z = key['host']
                self.nm.scan(hosts=z, arguments='-n -sP -PE -PA22')
                hosts_list: list[tuple[str, Any]] = [
                    (x, self.nm[x]['status']['state'])
                    for x in self.nm.all_hosts()
                ]
                # logger.debug(hosts_list)
                for ip_address, status in hosts_list:
                    try:
                        resolved = socket.gethostbyaddr(str(ip_address))
                        host_name = resolved[0]
                    except socket.error:
                        host_name = 'Unknown'
                    mac_address: str = arpreq.arpreq(ip_address)
                    Status = status.upper()
                    """
                    logger.info(
                        '{0}:{1}:{2}:{3}',
                        ip_address,
                        Status,
                        mac_address,
                        host_name,
                    )
                    """
                    self.lst.append(
                        [
                            GeneralFunctions.datetimestring(),
                            str(ip_address),
                            host_name,
                            '/32',
                            'check',
                            key['type'],
                            Status,
                            mac_address + ' Found',
                            key['last_down'],
                            key['last_up'],
                        ]
                    )
        # logger.info(self.lst)
        if any(elem is None for elem in self.lst):
            logger.error('None Found self.lst')

        # This is a list of lists containing all the IP addresses that do not
        # respond to arp request, along with the table entries for last_down
        # and last_up
        # host_name: str = ''
        ip_address_failed_arp: list = DatabaseActions.getfailedarp(conn_str)
        # logger.info(ip_address_failed_arp)
        # last_up = 'bugger'
        # last_down = 'bugger'
        if ip_address_failed_arp is not None:
            # logger.warning("failed arp: " + str(ip_address_failed_arp))
            for failed_arp in ip_address_failed_arp:
                # logger.info(failed_arp)
                ip_address = failed_arp[0]
                # last_down = failed_arp[1]
                last_up = failed_arp[2]
                try:
                    resolved = socket.gethostbyaddr(ip_address)
                    host_name = resolved[0]
                    # logger.info('{0}: {1}', 'Failed', host_name)
                except socket.error:
                    host_name = 'Unknown'
                # logger.info(failed_arp[1])
                # logger.info(failed_arp[2])
                if not failed_arp[1]:
                    last_down = GeneralFunctions.datetimestring()
                    logger.info('{0}:{1}', 'Not Failed ', host_name)
                else:
                    last_down = failed_arp[1]
                if not failed_arp[2]:
                    last_up = GeneralFunctions.datetimestring()
                else:
                    last_down = failed_arp[2]
                Status = 'DOWN'
                Reason = 'ARP Discovered (but now down)'
                self.lst.append(
                    [
                        GeneralFunctions.datetimestring(),
                        str(ip_address),
                        host_name,
                        '/32',
                        'check',
                        key['type'],
                        Status,
                        Reason,
                        last_down,
                        last_up,
                    ]
                )
        # logger.info(self.lst)
        if any(elem is None for elem in self.lst):
            logger.error('None Found self.lst')

        #  Wrap it all up and send the dataframe back
        # logger.info(self.lst)
        data_frame = pd.DataFrame(
            self.lst,
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
        # logger.info(MAGENTA + "----------" + RESET)
        # logger.info(MAGENTA + self.fred + RESET)
        # z = self.db.insertValue(self, self.lst)
        # th pd.option_context("display.max_rows", None, "display.max_columns", None):

        dataframe = data_frame.fillna('DOWN')
        # logger.info(dataframe)
        return dataframe


if __name__ == '__main__':
    """
    Form a complex number.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """
    conn_str = 'sqlite:///hoststatus.db'
    table_name = 'arp_status_table'
    toml_config = toml.load('app.config.toml')
    logger.info(toml_config)

    b = DiscoveredHostData(conn_str, table_name)
    c = b.queryDiscoveredhosts('sqlite:///hoststatus.db', toml_config)
    # logger.info(c)
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

"""
for ip_address in ipaddress.IPv4Network(key["host"]):
    mac_address: str = arpreq.arpreq(ip_address)
    if mac_address is not None:
        # descriptive_name = "NET"
        try:
            # self.app.logger.info(str(ip))
            host = socket.gethostbyaddr(str(ip_address))
            host_name = host[0]
            Status = "UP"
            logger.info("resolved: " +host_name + " " + mac_address)
        except socket.error:
            host_name = "Unknown"
            Status = "DOWN"
            logger.info("no resolved for: " + str(ip_address))
"""
