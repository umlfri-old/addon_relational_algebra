#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

if sys.platform == "win32":
    sys.path.insert(0, os.getcwd() + "\\share\\addons\\DRA\\libs")

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

    def connect(self, host1, database1, user1 ,password1, type, menu, windows, user2=None, password2=None):
        p = WaitingBar(self)
        windows.append(p)
        gobject.idle_add(p.show_all)
        if type is 0:
            try:
                self.__database = MySQLdb.connect(host=host1, user=user1, passwd=password1, db=database1)
            except MySQLdb.OperationalError as e:
                a = InfoBarDemo('Connection error',e.__str__(),"Warning",menu)
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
            con = 'belas/maxik8245@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=asterix.fri.uniza.sk)(PORT=1521)))(CONNECT_DATA=(SID=orcl)))'
            self.__database = cx_Oracle.connect(con)
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
                self.__database = psycopg2.connect(host=host1, dbname=database1, user=user1, password=password1)
                self.__database.set_isolation_level(0)
            except psycopg2.OperationalError as e:
                a = InfoBarDemo("Connection error", e.__str__(), "Warning", menu)
                windows.append(a)
                gobject.idle_add(p.hide_all)
                if self.__typ is not None:
                    gobject.idle_add(a.show)
                return
            self.__typ="postgreSQL"
            for m in menu:
                if m.gui_id == "connect":
                    m.visible = False
                if m.gui_id == "disconnect":
                    m.visible = True
                if m.gui_id == "execute":
                    m.enabled = True
            gobject.idle_add(p.hide_all)
        else:
            gobject.idle_add(p.hide_all)
            print "Nespravne pripojenie"

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
