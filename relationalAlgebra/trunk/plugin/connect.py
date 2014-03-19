#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

if sys.platform == "win32":
    sys.path.append(os.getcwd() + "\\share\\addons\\DRA\\libs")

try:
    import MySQLdb
except ImportError:
    MySQLdb = None

try:
    import psycopg2
except ImportError:
    psycopg2 = None

import psycopg2
try:
    import cx_Oracle
except ImportError:
    cx_Oracle = None

import gobject
from composite_operations import CompileError


from attention import *
from progress import WaitingBar

def Singleton(cls):
    instance = {}
    def getinstance():
        if cls not in instance:
            instance[cls] = cls()
        return instance[cls]
    return getinstance

@Singleton
class Connection():
    def __init__(self):
        self.__typ = ""
        self.__type = []

    def disconnect(self):
        self.__typ = None
        self.__type = []

    def getAvailableDatabases(self):
        databases = []
        if MySQLdb is not None:
            databases.append("MySQL")
        if cx_Oracle is not None:
            databases.append("Oracle")
        if psycopg2 is not None:
            databases.append("PostgreSQL")

        return databases

    def connect(self, host1, database1, user1 ,password1,sid, port, type, menu, windows):
        p = WaitingBar(self)
        windows.append(p)
        gobject.idle_add(p.show_all)
        if type is 0:
            try:
                port = int(port)
                self.__database = MySQLdb.connect(host=host1, user=user1, passwd=password1, db=database1, port=port)
            except ValueError:
                try:
                    self.__database = MySQLdb.connect(host=host1, user=user1, passwd=password1, db=database1)
                except MySQLdb.OperationalError as e:
                    a = InfoBarDemo('Connection error',e.__str__(),"Warning", menu)
                    windows.append(a)
                    gobject.idle_add(p.hide_all)
                    if self.__typ is not None:
                        gobject.idle_add(a.show)
                    return
            except MySQLdb.OperationalError as e:
                a = InfoBarDemo('Connection error',e.__str__(),"Warning", menu)
                windows.append(a)
                gobject.idle_add(p.hide_all)
                if self.__typ is not None:
                    gobject.idle_add(a.show)
                return
            self.__typ = "mysql"
            for m in menu:
                if m.gui_id == "connect":
                    m.visible = False
                if m.gui_id == "disconnect":
                    m.visible = True
                if m.gui_id == "execute":
                     m.enabled = True
            gobject.idle_add(p.hide_all)
        elif type is 1:
            try:
                con = '{0}/{1}@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST={2})(PORT={3})))(CONNECT_DATA=(SID={4})))'.format(user1,password1,host1,int(port),sid)
            except ValueError:
                a = InfoBarDemo("Connection error", "Please enter the port number", "Warning", menu)
                windows.append(a)
                gobject.idle_add(p.hide_all)
                if self.__typ is not None:
                    gobject.idle_add(a.show)
                return
            try:
                self.__database = cx_Oracle.connect(con)
            except cx_Oracle.DatabaseError as e:
                a = InfoBarDemo("Connection error", e.__str__(), "Warning", menu)
                windows.append(a)
                gobject.idle_add(p.hide_all)
                if self.__typ is not None:
                    gobject.idle_add(a.show)
                return
            self.__typ = "oracle"
            for m in menu:
                if m.gui_id == "connect":
                    m.visible = False
                if m.gui_id == "disconnect":
                    m.visible = True
                if m.gui_id == "execute":
                     m.enabled = True
            gobject.idle_add(p.hide_all)
        elif type is 2:
            #pripojenie na postreSQL
            try:
                port = int(port)
                self.__database = psycopg2.connect(host=host1, dbname=database1, user=user1, password=password1, port=port)
            except ValueError:
                try:
                    self.__database = psycopg2.connect(host=host1, dbname=database1, user=user1, password=password1)
                except psycopg2.OperationalError as e:
                    a = InfoBarDemo("Connection error", e.__str__(), "Warning", menu)
                    windows.append(a)
                    gobject.idle_add(p.hide_all)
                    if self.__typ is not None:
                        gobject.idle_add(a.show)
                    return
            except psycopg2.OperationalError as e:
                a = InfoBarDemo("Connection error", e.__str__(), "Warning", menu)
                windows.append(a)
                gobject.idle_add(p.hide_all)
                if self.__typ is not None:
                    gobject.idle_add(a.show)
                return
            self.__database.set_isolation_level(0)
            self.__typ="postgreSQL"
            for m in menu:
                if m.gui_id == "connect":
                    m.visible = False
                if m.gui_id == "disconnect":
                    m.visible = True
                if m.gui_id == "execute":
                     m.enabled = True
            gobject.idle_add(p.hide_all)


    def write_command(self, command):
        self.__stdin.write(command)
        line = self.__stdout.readline()
        while line != "#~#~#~#~#~#~#~#~#\n":
            line = self.__stdout.readline()

    def getTyp(self):
        return self.__typ

    def getColumns(self,table):
        self.__type=[]
        if self.__typ == "oracle":
            prikaz = "SELECT column_name FROM USER_TAB_COLUMNS WHERE table_name = '"+table.upper()+"'"
        elif self.__typ == "postgreSQL":
            prikaz = "SELECT column_name FROM information_schema.columns WHERE table_name ="+"'"+table+"';"
        else:
            prikaz = "SHOW COLUMNS IN "+table+";"
        cursor = self.__database.cursor()
        try:
            cursor.execute(prikaz)
        except MySQLdb.ProgrammingError as e:
            raise CompileError(e.__str__(), "Compile error")
        except psycopg2.ProgrammingError as e:
            raise CompileError(e.__str__(), "CompileError")

        header = []
        i = 0
        cursor = list(cursor)
        if self.__typ == "postgreSQL":
            for y in range(len(cursor)-1, -1, -1):
                for column in cursor[y]:
                    if i is 0:
                        header.append(column.lower())
                    i += 1
                i = 0
        else:
            for y in range(0, len(cursor)):
                for column in cursor[y]:
                    if i is 0:
                        header.append(column.lower())
                    i += 1
                i = 0
        return header

    def getData(self,table):
        prikaz = "SELECT * FROM "+table
        cursor = self.__database.cursor()
        try:
            cursor.execute(prikaz)
        except MySQLdb.ProgrammingError as e:
            raise CompileError(e.__str__(), "CompileError")
        except psycopg2.ProgrammingError as e:
            raise CompileError(e.__str__(), "CompileError")
        data = list(cursor)
        return data
