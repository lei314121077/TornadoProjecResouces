#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging


class Mysqldb(object):
    def __conn(self):
        if self.conn is None:
            from sys import modules
            if 'bae' in modules:
                from bae.core import const
                dbconf = {
                    'user': const.MYSQL_USER,
                    'passwd': const.MYSQL_PASS,
                    'db': 'NtwLDxlnbZIsMEPsgrFH',
                    'host' : const.MYSQL_HOST,
                    'port' : int(const.MYSQL_PORT),
                    'charset' : self.charset
                }
                import MySQLdb
                connect = MySQLdb.connect
            elif 'sae' in modules:
                from sae import const
                dbconf = {
                    'user': const.MYSQL_USER,
                    'passwd': const.MYSQL_PASS,
                    'db': const.MYSQL_DB,
                    'host': const.MYSQL_HOST,
                    'port': int(const.MYSQL_PORT),
                    'charset': self.charset
                }
                import MySQLdb
                connect = MySQLdb.connect
            else:
                dbconf = {'database': r'd:/weicbd_db.sqlite3'}
                print(dbconf)
                import sqlite3
                connect = sqlite3.connect

            self.conn = connect(**dbconf)
        return self.conn

    def __init__(self):
        self.charset = 'utf8'
        self.conn = None

    def commit(self):
        self.__conn().commit()

    def close(self):
        self.__conn().close()

    def execute(self, sql, arg=None):
        cursor = self.__conn().cursor()
        cursor.execute(sql, arg or tuple())
        cursor.close()
        return cursor.lastrowid

    def executemany(self, sql, arg):
        cursor = self.__conn().cursor()
        cursor.executemany(sql, arg or tuple())
        cursor.close()

    def rollback(self):
        self.__conn().rollback()

    def select(self, sql, arg=None):
        cursor = self.__conn().cursor()
        cursor.execute(sql, arg or tuple())
        for r in cursor:
            try:
                yield r
            except GeneratorExit:
                cursor.close()
            # cursor.close()

    def fetchone(self, sql, arg=None):
        cursor = self.__conn().cursor()
        cursor.execute(sql, arg or tuple())
        rt = cursor.fetchone()
        # cursor.close()
        return rt

    def fetchall(self, sql, arg=None):
        cursor = self.__conn().cursor()
        cursor.execute(sql, arg or tuple())
        for r in cursor.fetchall():
            try:
                yield r
            except GeneratorExit:
                cursor.close()

    def __create(self, cur):
        pass

    def __del__(self):
        if self.conn is not None:
            self.conn.close()


def get_log_list():
    import model.logging
    from orm import getSession
    return getSession().query(model.logging.Logging).order_by(model.logging.Logging.id.desc()).limit(100)
    # db = Mysqldb()
    # return db.fetchall('''
    #     SELECT content FROM cloud_logger ORDER BY tm desc limit 0, 50
    # ''')


def getLogger():
    logger = logging.getLogger('cloud_logger')
    logger.setLevel(logging.DEBUG)

    if len(logger.handlers) == 0:
        ch = DBLoggingHandler()
        ch.setLevel(logging.INFO)
        ch_format = logging.Formatter('<div><p>%(asctime)s - %(levelname)s</p><xmp>%(message)s</xmp></div>')
        ch.setFormatter(ch_format)
        logger.addHandler(ch)

    return logger


class DBLoggingHandler(logging.Handler):
    def __init__(self):
        super(DBLoggingHandler, self).__init__()

    def emit(self, record):
        try:
            msg = self.format(record)
            import model.logging
            from orm import getSession
            session = getSession()
            l = model.logging.Logging(msg)
            session.add(l)
            session.commit()
        except:
            self.handleError(record)


def log(msg):
    getLogger().info(msg)
    return msg