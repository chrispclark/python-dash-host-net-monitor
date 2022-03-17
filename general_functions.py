#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 13:50:11 2021

@author: chrissy
"""

from flask_loguru import logger
from datetime import datetime
from plyer import notification
import ipaddress
import socket


class LogManager:
    """
    Summary.

    Returns
    -------
    None.

    """

    def __init__(self, filename, mode):
        """
        Summary.

        Returns
        -------
        None.

        """
        self.filename = filename
        self.mode = mode
        self.file = None
        # logger.info("file init")

    def __enter__(self):
        """
        Summary.

        Returns
        -------
        None.

        """
        # logger.info("file enter")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Summary.

        Returns
        -------
        None.

        """
        # logger.info("file exit")
        self.file.close()


class GeneralFunctions:
    @staticmethod
    def datetimestring():
        return f'{datetime.now():%d/%m/%Y %H:%M:%S}'

    @staticmethod
    def send_notification(title, message):
        notification.notify(title, message)

    @staticmethod
    def writeIt(filename, mode, alert):
        dt_string: str = GeneralFunctions.datetimestring()
        with LogManager(filename, mode) as log_file:
            log_file.write(dt_string + ' Moved to down: ' + alert)
            log_file.write('\n')
        GeneralFunctions.send_notification('ALERT', alert)

    @staticmethod
    def validate_ip_address(ipAddress):
        try:
            return socket.gethostbyaddr(ipAddress)
        except socket.error:
            return None, None, None


if __name__ == '__main__':
    """
    Form a complex number.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """
    z = GeneralFunctions.validate_ip_address('fred')
    logger.info(z)
    search = 'host_search'
    dt_string = GeneralFunctions.datetimestring()
    logdata = dt_string + ' Moved to down: ' + search
    GeneralFunctions.writeIt('logfile.txt', 'a', logdata)
