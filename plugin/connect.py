#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import paramiko
import psycopg2
from error import *
import dateutil
import re
from dateutil.relativedelta import relativedelta
import datetime,time
from operations import parse_time
def Singleton(cls):
    instance = {}
    def getinstance():
        if cls not in instance:
            instance[cls]=cls()
        return instance[cls]
    return getinstance

@Singleton
class Connection():
    def __init__(self):
        self.__typ=""
        self.__type=[]
    def disconnect(self):
        self.__typ=""
        self.__type=[]
    def connect(self,host1,database1,user1,password1,type,user2=None,password2=None):
        if type is 0:
            try:
                self.__database= MySQLdb.connect(host=host1,user=user1,passwd=password1,db=database1)
            except MySQLdb.OperationalError as e:
                raise CompileError(e.__str__(),"Connection error")
            self.__typ="mysql"
        elif type is 1:
            #pripojenie na oracle
            self.__database = paramiko.SSHClient()
            self.__database.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if user2 is None:
                try:
                    user=user1.rsplit("@")
                    self.__database.connect(host1, username=user[0],password=password1)
                except paramiko.AuthenticationException as e:
                    raise CompileError(e.__str__()+ " Login or password to server is wrong","Connection error")
                except Exception as e:
                    if e.__str__()=="[Errno 11004] getaddrinfo failed":
                        raise CompileError("Connect to database failed. Unknown server "+ host1,"Connection error")
                    else:
                        raise CompileError("Cannot connect to server","Connection error")
            else:
                try:
                    self.__database.connect(host1, username=user2,password=password2)
                except paramiko.AuthenticationException as e:
                    raise CompileError(e.__str__()+" Login or password to server is wrong","Connection error")
                except Exception as e:
                    if e.__str__()=="[Errno 11004] getaddrinfo failed":
                        raise CompileError("Connect to database failed. Unknown server "+ host1,"Connection error")
                    else:
                        raise CompileError("Cannot connect to server","Connection error")
            command='bash -l -c "sqlplus '+user1+"\""
            self.__stdin,self.__stdout,self.__stderr=self.__database.exec_command(command)
            if not self.__stdout.readline():
                string=self.__stderr.readlines()
                if "bash: sqlplus:" in string[0]:
                    raise CompileError("Oracle database not installed on server","Connection error")
                else:
                    raise CompileError("Connect to database failed","Connection error")
            self.__stdin.write(password1)
            self.__stdin.write('col c new_value cnv;\n')
            self.__stdin.write('select chr(10) c from dual;\n')
            self.__stdin.write('set sqlprompt "#~#~#~#~#~#~#~#~# cnv";\n')

            line=self.__stdout.readline()
            while line!="SQL> #~#~#~#~#~#~#~#~#\n":
                if line=="ERROR:\n":
                    raise CompileError("Database authentication error. Login or password to database is wrong. Login must be in format for example login@orcl","Connection error")
                line=self.__stdout.readline()
            self.write_command('set pages 0;\n')
            self.write_command('set recsep ea;\n')
            self.write_command('set space 10;\n')
            self.write_command('set tab on;\n')
            self.write_command('set colsep ||;\n')
            self.write_command('set linesize 32767 ||;\n')
            self.write_command('alter session set NLS_TIMESTAMP_FORMAT="YYYY-MM-DD HH24:MI:SS";\n')
            self.write_command('alter session set NLS_DATE_FORMAT="YYYY-MM-DD";\n')
            self.__typ="oracle"
        elif type is 2:
            #pripojenie na postreSQL
            try:
                self.__database=psycopg2.connect(host=host1,dbname=database1,user=user1,password=password1)
                self.__database.set_isolation_level(0)
            except psycopg2.OperationalError as e:
                raise CompileError(e.__str__(),"Connection error")
            self.__typ="postgreSQL"
        else:
            print "Nespravne pripojenie"
    def write_command(self,command):
        self.__stdin.write(command)
        line=self.__stdout.readline()
        while line!="#~#~#~#~#~#~#~#~#\n":
            line=self.__stdout.readline()
    def getTyp(self):
        return self.__typ
    def getColumns(self,table):
        self.__type=[]
        if self.__typ=="oracle":
            prikaz="desc " + table+";\n"
            self.__stdin.write(prikaz)
            lines=[]
            names=[]
            line=self.__stdout.readline()
            if line == "ERROR:\n":
                raise CompileError("Table "+ table+" doesnt exist.","Compile error")
            while line!="#~#~#~#~#~#~#~#~#\n":
                lines.append(line)
                line=self.__stdout.readline()
            del lines[0]
            del lines[0]
            lines.remove("\n")
            while len(lines):
                line=lines[0].rsplit("\t")
                i=0
                while line[i]=='':
                    i +=1
                names.append([line[i],line[-1]])
                del lines[0]
            header=[]
            for name in names:
                new=[]
                name_column=name[0].lower()
                type=name[-1]
                #0-type string
                #1-type number
                #2-date
                #3-timestamp
                #4-interval year-month
                #5-interval day-seconds
                if "INTEGER" in type or "NUMBER" in type:
                    type=1
                elif "DATE" in type:
                    type=2
                elif "TIME" in type:
                    type=3
                elif "INTERVAL YEAR" in type:
                    type=4
                elif "INTERVAL DAY" in type:
                    type=5
                else:
                    type=0
                self.__type.append(type)
                name_column=' '.join(name_column.split())
                new.append(name_column)
                str=table+"."+name_column
                new.append(str)
                header.append(new)
            return header
        else:
            if self.__typ=="postgreSQL":
                prikaz="SELECT column_name FROM information_schema.columns WHERE table_name ="+"'"+table+"';"
            else:
                prikaz="SHOW COLUMNS IN "+table+";"
            cursor=self.__database.cursor()
            cursor.execute(prikaz)
            header=[]
            i=0
            cursor=list(cursor)
            if self.__typ=="postgreSQL":
                for y in range(len(cursor)-1,-1,-1):
                    new=[]
                    for column in cursor[y]:
                        if i is 0:
                            new.append(column.lower())
                            str=table+"."+column.lower()
                            new.append(str)
                        i += 1
                    header.append(new)
                    i=0
            else:
                for y in range(0,len(cursor)):
                    new=[]
                    for column in cursor[y]:
                        if i is 0:
                            new.append(column.lower())
                            str=table+"."+column.lower()
                            new.append(str)
                        i += 1
                    header.append(new)
                    i=0
            return header
    def getData(self,table):
        prikaz="SELECT * FROM "+table+";\n"
        if self.__typ=="oracle":
            self.__stdin.write(prikaz)
            line=self.__stdout.readline()
            lines=[]
            while line!="#~#~#~#~#~#~#~#~#\n":
                lines.append(line)
                line=self.__stdout.readline()
            data=[]
            i=-1
            end=False
            while not end:
                i +=1
                string=""
                while lines[i]!="\n":
                    string=string+lines[i]
                    i +=1
                data.append(string)
                try:
                    if lines[i+1]=="\n":
                        end=True
                except IndexError:
                    raise CompileError("Table "+table+" is empty","Table error in "+table)
            cursor=[]
            new=[]
            for row in data:
                row=row.replace("\n"," ||")
                new=[]
                columns=row.rsplit('||')
                for i in range(len(columns)-1,-1,-1):
                    if columns[i]=="":
                        del columns[i]
                for i in range(0,len(columns)):
                    column=' '.join(columns[i].split())
                    if column=="":
                        column=None
                    elif self.__type[i] is 1:
                        try:
                            column=int(column)
                        except ValueError:
                            try:
                                column=float(column)
                            except ValueError:
                                raise ValueError
                    elif self.__type[i] is 2:
                        time_format = "%Y-%m-%d"
                        column = datetime.date.fromtimestamp(time.mktime(time.strptime(column, time_format)))
                    elif self.__type[i] is 3:
                        time_format = "%Y-%m-%d %H:%M:%S"
                        column = datetime.datetime.fromtimestamp(time.mktime(time.strptime(column, time_format)))
                    elif self.__type[i] is 4:
                        #datatype interval year to month
                        try:
                            data=re.findall("\d+", column)
                            for i in range(0,len(data)):
                                    data[i]=int(data[i])
                            column=relativedelta(years=data[0],months=data[1])
                        except Exception:
                            raise CompileError("Format of 'year to month' returned from database is wrong","Database error")
                    elif self.__type[i] is 5:
                        try:
                            column=parse_time(column)
                        except Exception as e:
                            raise CompileError("Format of 'interval month to day' returned from database is wrong","Database error")
                    new.append(column)
                cursor.append(new)
            return cursor
        else:
            cursor=self.__database.cursor()
            cursor.execute(prikaz)
            return cursor
