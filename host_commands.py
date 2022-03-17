#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 12:06:22 2021

@author: chrissy
"""

import socket
import sys
from ipaddress import IPv4Address

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import dns.resolver
import dns.reversename
import ipaddress
import arpreq
from general_functions import GeneralFunctions
import toml

# from loguru import logger
from flask_loguru import logger
import coloredlogs

coloredlogs.install()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


class GeneralCommands:
    """
    Summary.

    Returns
    -------
    None.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    def __init__(self, toml_config_dict):
        """`
        Summary.

        Returns
        -------
        None.

        """
        self.toml_config_dict = toml_config_dict
        self.isDiscoveryRunning = False
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }


    @staticmethod
    def reversedns(dnsserver, ipaddress) -> dns.name.Name:
        """
        Summary.

        Returns
        -------
        None.

        """
        logger.info(dnsserver)
        # logger.info(ipaddress)
        # dnsserver = "conservatory-media.chrissy.org."
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = [dnsserver]
        domain_address = dns.reversename.from_address(ipaddress)
        # logger.info(domain_address)
        # domain_name = str(dns.resolver.resolve(domain_address, "PTR")[0])
        # logger.info(domain_name)
        # logger.debug(type(domain_address))
        # logger.debug(domain_address)
        return domain_address

    @staticmethod
    def url(url):
        """
        Summary.

        Returns
        -------
        None.

        """
        try:
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += (
                'HIGH:!DH:!aNULL'
            )
            s = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            page = s.get(url, headers=headers, timeout=10)
            if page.status_code == 200:
                status = 'UP'
            else:
                status = page.status_code[0:10]
        except Exception as e:
            logger.warning(e)
            status = e
        return str(status)

    # pylint: disable=no-self-use

    @staticmethod
    def hostportcheck(address, port) -> str:
        """
        Summary.

        Returns
        -------
        None.

        """
        ip = address
        # port = 22
        # retry = 1
        # delay = 1
        timeout = 5
        # a = ""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((ip, int(port)))
            s.shutdown(socket.SHUT_RDWR)
            a = 'UP'
        except socket.error:
            a = 'DOWN'
        finally:
            s.close()
        return a


if __name__ == '__main__':
    toml_config = toml.load('app.config.toml')
    b = GeneralCommands(toml_config)
    b.reversedns('127.0.0.1', '192.168.1.77')
