#!/usr/bin/python
import MySQLdb

def singleton(cls):
    instance = {}
    def getinstance():
        if cls not in instance:
            instance[cls]=cls()
        return instance[cls]
    return getinstance

@singleton
class Connection:
    def __init__(self,typ):
        if typ == 1:
            self.Database= MySQLdb.connect(host="localhost",user="belas",passwd="824510802",db="skuska")
            self.typ="mysql"
        elif typ == 2:
            #pripojenie na oracle
            self.typ="oracle"
        elif typ == 3:
            #pripojenie na postreSQL
            self.typ="postgreSQL"
        else:
            print "Nespravne pripojenie"




