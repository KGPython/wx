# -*-  coding:utf-8 -*-
# __author__ = ''
# __date__ = '2017/4/21 13:43'
import pymssql
import pymysql

from utils import consts


def getMsSqlConn(as_dict=True):
    conn = pymssql.connect(
        host=consts.DB_SERVER_226,
        port=consts.DB_PORT_226,
        user=consts.DB_USER_226,
        password=consts.DB_PASSWORD_226,
        database=consts.DB_DATABASE_226,
        charset='utf8',
        as_dict=as_dict
    )
    return conn

def getMsSqlConn22(as_dict=True):
    conn = pymssql.connect(
        host=consts.DB_SERVER_22,
        port=consts.DB_PORT_22,
        user=consts.DB_USER_22,
        password=consts.DB_PASSWORD_22,
        database=consts.DB_DATABASE_22,
        charset='utf8',
        as_dict=as_dict
    )
    return conn


def getMysqlConn():
    conn = pymysql.connect(
        host=consts.DB_SERVER_9,
        port=consts.DB_PORT_9,
        user=consts.DB_USER_9,
        password=consts.DB_PASSWORD_9,
        db=consts.DB_DATABASE_9,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn


def getMysqlConn2():
    conn = pymysql.connect(
        host=consts.DB_SERVER_187,
        port=consts.DB_PORT_187,
        user=consts.DB_USER_187,
        password=consts.DB_PASSWORD_187,
        db=consts.DB_DATABASE_187,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn


def getMysqlConnection(host, port, user, password, db):
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def getMsSqlConnection(host, port, user, password, db,as_dict=True):
    conn = pymssql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db,
        charset='utf8',
        as_dict=as_dict
    )
    return conn
