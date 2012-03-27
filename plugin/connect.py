#!/usr/bin/python
import MySQLdb
import paramiko
import psycopg2


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
        self.__type=[]
    def connect(self,host1,database1,user1,password1,type,user2=None,password2=None):
        if type is 0:
            self.__database= MySQLdb.connect(host=host1,user=user1,passwd=password1,db=database1)
            self.__typ="mysql"
        elif type is 1:
            #pripojenie na oracle
            self.__database = paramiko.SSHClient()
            self.__database.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__database.connect(host1, username=user1,password=password1)
            if user2 is None:
                command='bash -l -c "sqlplus '+user1+"/"+password1+"@orcl\""
            else:
                command='bash -l -c "sqlplus '+user2+"/"+password2+"@orcl\""
            print command
            self.__stdin,self.__stdout,self.__stderr=self.__database.exec_command(command)
            self.__stdin.write('col c new_value cnv;\n')
            self.__stdin.write('select chr(10) c from dual;\n')
            self.__stdin.write('set sqlprompt "#~#~#~#~#~#~#~#~# cnv";\n')
            line=self.__stdout.readline()
            while line!="SQL> #~#~#~#~#~#~#~#~#\n":
                line=self.__stdout.readline()
            self.__typ="oracle"
        elif type is 2:
            #pripojenie na postreSQL
            self.__database=psycopg2.connect(host=host1,database=database1,user=user1,password=password1)
            self.__typ="postgreSQL"
        else:
            print "Nespravne pripojenie"
    def disconnect(self):
        self.__typ=""
    def getTyp(self):
        return self.__typ
    def getColumns(self,table):
        if self.__typ=="oracle":
            prikaz="desc " + table+";\n"
            self.__stdin.write(prikaz)
            lines=[]
            names=[]
            line=self.__stdout.readline()
            while line!="#~#~#~#~#~#~#~#~#\n":
                lines.append(line)
                line=self.__stdout.readline()
            del lines[0]
            del lines[0]
            lines.remove("\n")
            while len(lines):
                line=lines[0].rsplit(" ")
                i=0
                while line[i]=='':
                    i +=1
                names.append([line[i],line[-1]])
                del lines[0]
            header=[[],[]]
            for name in names:
                name_column=name[0]
                type=name[1]
                #0-type string
                #1-type integer
                #2-type float
                if "INTEGER" in type or "NUMBER" in type:
                    pass
                self.__type.append(type)
                name_column=' '.join(name_column.split())
                header[0].append(name_column)
                str=table+"."+name_column
                header[1].append(str)
            return header
        else:
            if self.__typ=="postgreSQL":
                prikaz="SELECT column_name FROM information_schema.columns WHERE table_name ="+"'"+table+"';"
            else:
                prikaz="SHOW COLUMNS IN "+table+";"
            cursor=self.__database.cursor()
            cursor.execute(prikaz)
            header=[[],[]]
            i=0
            for row in cursor:
                for column in row:
                    if i is 0:
                        header[0].append(column)
                        str=table+"."+column
                        header[1].append(str)
                    i += 1
                i=0
            return header
    def getData(self,table):
        prikaz="SELECT * FROM "+table+";"
        if self.__database=="oracle":
            self.__stdin.write(prikaz)
            line=self.__stdout.readline()
            if line=="/n":
                pass
            else:
                raise Exception
        else:
            cursor=self.__database.cursor()
            cursor.execute(prikaz)
            return cursor
