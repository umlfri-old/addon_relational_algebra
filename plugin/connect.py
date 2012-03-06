#!/usr/bin/python
import MySQLdb

def Singleton(cls):
    instance = {}
    def getinstance():
        if cls not in instance:
            instance[cls]=cls()
        return instance[cls]
    return getinstance

@Singleton
class Connection:
    def __init__(self):
        self.__typ=""
    def pripoj(self,druh):
        if druh == 0:
            self.__database= MySQLdb.connect(host="localhost",user="root",passwd="maxik8245",db="cars")
            self.__typ="mysql"
        elif druh == 1:
            #pripojenie na oracle
            raise ValueError
        elif druh == 2:
            #pripojenie na postreSQL
            self.__typ="postgreSQL"
        else:
            print "Nespravne pripojenie"
    def disconnect(self):
        self.__typ=""
    def getTyp(self):
        return self.__typ
    
    def dajData(self,tabulka):
        prikaz='SELECT * FROM ' + tabulka
        cursor=self.__database.cursor()
        cursor.execute(prikaz)
        return cursor
    def vykonaj(self,prikaz):
        cursor=self.__database.cursor()
        cursor.execute(prikaz)
        return cursor
