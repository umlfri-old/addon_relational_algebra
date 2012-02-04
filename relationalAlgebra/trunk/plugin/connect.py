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
    def pripoj(self,druh):
        if druh == 1:
            self.__database= MySQLdb.connect(host="localhost",user="belas",passwd="824510802",db="skuska")
            self.__typ="mysql"
        elif druh == 2:
            #pripojenie na oracle
            self.__typ="oracle"
        elif druh == 3:
            #pripojenie na postreSQL
            self.__typ="postgreSQL"
        else:
            print "Nespravne pripojenie"

    def getTyp(self):
        print self.__typ

    def dajData(self,tabulka):
        prikaz='SELECT * FROM ' + tabulka
        cursor=self.__database.cursor()
        cursor.execute(prikaz)
        return cursor
    
