#!/usr/bin/env python3
# -*- coding: utf-8 -*-.
"""
Created on Fri May  7 15:53:58 2021.

@author: chrissy
"""
# from sqlalchemy import create_engine, MetaData, Column, Integer, String
# from sqlalchemy import inspect
# from sqlalchemy.orm import sessionmaker, scoped_session

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, UniqueConstraint

# from sqlalchemy.ext.automap import automap_base
# from loguru import logger
from flask_loguru import logger

# from sqlalchemy.ext.declarative import declarative_base

conn_str = 'sqlite:///hoststatus.db'


class SQLModelDBConnection(object):
    """
    Form a complex number.

    Keyword arguments:
    real -- the real part (default 0.0)
    imag -- the imaginary part (default 0.0)
    """

    def __init__(self, connection_string):
        """
        Form a complex number.

        Keyword arguments:
        real -- the real part (default 0.0)
        imag -- the imaginary part (default 0.0)
        """
        # logger.info("init: " + connection_string)
        self.connection_string = connection_string
        self.session = None

    def __enter__(self):
        """
        Form a complex number.

        Keyword arguments:
        real -- the real part (default 0.0)
        imag -- the imaginary part (default 0.0)
        """
        # logger.info(self.connection_string)
        engine = create_engine(
            self.connection_string, echo=False, future=False
        )
        self.session = Session(bind=engine, expire_on_commit=False)
        # logger.info("session: " + str(self.session))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Form a complex number.

        Keyword arguments:
        real -- the real part (default 0.0)
        imag -- the imaginary part (default 0.0)
        """
        self.session.commit()
        self.session.close()
        # logger.info("exited")
        return 'committed'


class arp_status_table(SQLModel, table=True):
    """
    Define table to hold status.

    Keyword arguments:

    Returns:
    None
    """

    __table_args__ = (UniqueConstraint('descriptive_name'),)
    id: Optional[int] = Field(default=None, primary_key=True)
    DateAndTime: str
    descriptive_name: str = Field(index=True)
    host: str
    mask: str
    check: str
    type: str
    Status: str
    Reason: str
    last_down: str
    last_up: str

    def __repr__(self):
        """
        Form a complex number.

        Keyword arguments:
        real -- the real part (default 0.0)
        imag -- the imaginary part (default 0.0)
        """
        return '{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(
            self.id,
            self.DateAndTime,
            self.descriptive_name,
            self.host,
            self.mask,
            self.check,
            self.type,
            self.Status,
            self.Reason,
            self.last_down,
            self.last_up,
        )


sqlite_file_name = 'hoststatus.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'
engine = create_engine(sqlite_url, future=False, echo=False)
SQLModel.metadata.create_all(engine)


class host_status_table(SQLModel, table=True):
    """
    Define table to hold status.

    Keyword arguments:

    Returns:
    None
    """

    __table_args__ = (UniqueConstraint('descriptive_name'),)
    id: Optional[int] = Field(default=None, primary_key=True)
    DateAndTime: str
    descriptive_name: str = Field(index=True)
    host: str
    mask: str
    check: str
    type: str
    Status: str
    Reason: str
    last_down: str
    last_up: str

    def __repr__(self):
        """
        Form a complex number.

        Keyword arguments:
        real -- the real part (default 0.0)
        imag -- the imaginary part (default 0.0)
        """
        return '{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(
            self.id,
            self.DateAndTime,
            self.descriptive_name,
            self.host,
            self.mask,
            self.check,
            self.type,
            self.Status,
            self.Reason,
            self.last_down,
            self.last_up,
        )


sqlite_file_name = 'hoststatus.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'
engine = create_engine(sqlite_url, echo=False, future=False)
SQLModel.metadata.create_all(engine)
# meta = SQLModel.metadata

"""
z = host_status_table.__fields__.keys()
for j in list(z):
    print(j)
fruit_dictionary = dict.fromkeys(z, "In stock")
print(fruit_dictionary)
"""
if __name__ == '__main__':
    # z = host_status_table()
    y = arp_status_table()
    logger.info('here')

"""    
    #query_statement = select(host_status_table)
    # select([text("students.name, students.lastname from students")]).where(text("students.name between :x and :y"))
    x = TestIt()
    b = x.queryit()
    for a in b:
        logger.info(b)
    """
# Base.metadata.create_all(engine)
