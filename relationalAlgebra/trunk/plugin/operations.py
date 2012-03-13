import re
import copy
from relation import *
from row import *
class Table:
    def __init__(self,data,table):
        self.__database=data
        self.__table_name=table
    def execute(self):
        #return name of columns and store into variable header
        cursor=self.__database.vykonaj('SHOW COLUMNS IN ' +self.__table_name)
        #variable to store columns name with their table name
        header=[[],[]]
        i=0
        for row in cursor:
            for column in row:
                if i is 0:
                    header[0].append(column)
                    str=self.__table_name+"."+column
                    header[1].append(str)
                i += 1
            i=0
        #create new relation with columns name
        relation=Relation(header)
        #return data from table
        data=self.__database.dajData(self.__table_name)
        tem=list(data)
        #from all data create class row with columns name(columns name with their table name) and with data and add to relation
        for i in range(0,len(tem)):
            new=[]
            #na toto sa spytat aby header nebol stale odkaz na tu istu instanciu header ale aby kazdy row mal svoju vlastnu
            for y in range(0,len(header[0])):
                new.append(tem[i][y])
            header1=copy.deepcopy(header)
            relation.addRow(Row(new,header1))
        return relation
class Projection:
    def __init__(self,data):
        #attribute to store name of columns,which are selected from relation
        self.__data=[]
        a=data.rsplit(":")
        for i in range(1,len(a)):
            b=a[i].rsplit("'")
            self.__data.append(b[1])
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        #return relation of ancestor
        ret=self.__ancestor.execute()
        #store header
        header=ret.getHeader()
        indexes=[]
        #find and store into indexes columns numbers, which are selected
        #at first try to search in header[0](represented columns name without table_name) and then try to search
        #in header[1](represented columns name with table_name)
        for i in range(0,len(self.__data)):
            try:
                index=header[0].index(self.__data[i])
                indexes.append(index)
            except ValueError:
                try:
                    index=header[1].index(self.__data[i])
                    indexes.append(index)
                except ValueError:
                    return None

        #create new header with selected columns
        for i in range(len(header[0])-1,-1,-1):
            try:
                indexes.index(i)
            except ValueError:
                del header[0][i]
                del header[1][i]
        relation=Relation(header)
        #edit each row(delete columns which arent selected)
        for row in ret:
            for i in range(row.getLen()-1,-1,-1):
                try:
                    indexes.index(i)
                except ValueError:
                    row.deleteColumn(i)
            relation.addRow(row)
        return relation

class Selection:
    def __init__(self,column,condition,data):
        self.__column=column
        self.__condition=condition
        try:
            self.__data=float(data)
        except ValueError:
            self.__data=""
            if(data[0]=='"') and (data[-1]=='"') or (data[0]=="'" and data[-1]=="'"):
                for i in range(0,len(data)):
                    if (i!=0)&(i!=(len(data)-1)):
                        self.__data=self.__data+data[i]
            else:
                print "data error"
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        ret=self.__ancestor.execute()
        header=ret.getHeader()
        try:
            index=header[0].index(self.__column)
        except ValueError:
            try:
                index=header[1].index(self.__column)
            except ValueError:
                print "selection error"
                return None
        relation=Relation(header)
        for i in ret:
            if condition(i.getData(index),self.__data,self.__condition):
                relation.addRow(Row(i.getData(),i.getHeader()))
        return relation
class Product:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if self.__ancestor_left is None :
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        header=ret.getHeader()
        header1=ret1.getHeader()
        header_new=[[],[]]
        header_new[0]=header[0]+header1[0]
        header_new[1]=header1[1]+header1[1]
        relation=Relation(header_new)
        for i in ret:
            for y in ret1:
                new=i.getData()+y.getData()
                relation.addRow(Row(new,copy.deepcopy(header_new)))
        return relation
class Union:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if self.__ancestor_left is None :
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        header=ret.getHeader()
        header1=ret1.getHeader()
        print header
        print header1
        relation=Relation(header)
        if header[0]==header1[0]:
            for i in ret:
                relation.addRow(Row(i.getData(),i.getHeader()))
            for i in ret1:
                relation.addRow(Row(i.getData(),i.getHeader()))
        else:
            print "union incompatible error"
            return None
        return relation
class Intersection:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        header=ret.getHeader()
        header1=ret1.getHeader()
        relation=Relation(header)
        if header[0]==header1[0]:
           for i in ret:
               try:
                   ret1.getData().index(i.getData())
                   relation.addRow(Row(i.getData(),i.getHeader()))
               except ValueError:
                   pass
        else:
            print "intersection incompatible error"
            return None
        return relation
class Division:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        columns=ret[0]
        columns_help=columns
        columns1=ret1[0]
        table=[]
        indexes=[]
        indexes2=[]
        match={}
        for i in range(0,len(columns1)):
            try:
                indexes.append(columns.index(columns1[i]))
                columns.remove(columns1[i])
            except ValueError:
                print "division error"
                return None
        table.append(columns)
        for i in range(0,len(columns)):
            indexes2.append(columns_help.index(columns[i]))
        for i in range(1,len(ret)):
            string1=""
            for a in range(0,len(indexes)):
                string1=string1+","+ret[i][indexes[a]]
            for y in range(1,len(ret1)):
                string2=""
                for b in range(0,len(indexes)):
                    string2=string2+","+ret1[y][b]
                if string1==string2 :
                    string3=""
                    for c in range(0,len(indexes2)):
                        string3=string3+","+ret[i][c]
                    if match.get(string3) is None :
                        new=[]
                        new.append(i)
                        new.append(1)
                        match[string3]=new
                    else:
                        new=match.get(string3)
                        number=new[1]
                        new[1]=number+1
                        match[string3]=new
        values=match.values()
        for i in range(0,len(values)):
            new=values[i]
            if new[1]==(len(ret1)-1):
                row=new[0]
                new1=[]
                for y in range(0,len(indexes2)):
                    new1.append(ret[row][y])
                table.append(new1)
        return table
class Difference:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if self.__ancestor_left is None :
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        header=ret.getHeader()
        header1=ret1.getHeader()
        relation=Relation(header)
        if header[0]==header1[0]:
            for i in ret:
                try:
                    ret1.getData().index(i.getData())
                except ValueError:
                    relation.addRow(Row(i.getData(),i.getHeader()))
        else:
            print "difference error"
            return None
        return relation
class Inner_Join:
    def __init__(self,column1,condition,column2):
        self.__ancestor_left=None
        self.__ancestor_right=None
        self.__column1=column1
        self.__condition=condition
        self.__column2=column2
    def set(self,ancestor):
        if(self.__ancestor_left==None):
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def condition(self,column1,column2):
        if(self.__condition=="="):
            if(column1==column2):
                return True
            else:
                return False
        elif(self.__condition=="<"):
            if(column1<column2):
                return True
            else:
                return False
        elif(self.__condition==">"):
            if(column1>column2):
                return True
            else:
                return False
        elif(self.__condition=="<="):
            if(column1<=column2):
                return True
            else:
                return False
        elif(self.__condition==">="):
            if(column1>=column2):
                return True
            else:
                return False
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        columns=ret[0]
        columns1=ret1[0]
        try:
            index1=columns.index(self.__column1)
            index2=columns1.index(self.__column2)
        except:
            print "inner join error"
            return
        new_columns=columns+columns1
        table=[]
        table.append(new_columns)
        for i in range(1,len(ret)):
            for y in range(1,len(ret1)):
                if(self.condition(ret[i][index1],ret[y][index2])==True):
                    new=ret[i]+ret1[y]
                    table.append(new)
def condition(column1,column2,condition):
    if condition=="=" :
        if column1 == column2:
            return True
        else :
            return False
    elif condition=="<":
        if column1 == column2:
            return True
        else :
            return False
    elif condition==">":
        if column1 == column2:
            return True
        else :
            return False
    elif condition==">=":
        if column1 == column2:
            return True
        else :
            return False
    elif condition=="<=":
        if column1 == column2:
            return True
        else :
            return False
    elif condition=="!=":
        if column1 == column2:
            return True
        else :
            return False
    elif condition=="LIKE":
        regex=column2.replace(".","\\.\\")
        regex=regex.replace("*","\\*\\")
        regex=regex.replace("_",".")
        regex=regex.replace("%",".*")
        a=re.match(regex,column1)
        if a is not None :
            return True
        else:
            return False
    elif condition=="NOT LIKE" :
        regex=column2.replace(".","\\.\\")
        regex=regex.replace("*","\\*\\")
        regex=regex.replace("_",".")
        regex=regex.replace("%",".*")
        a=re.match(regex,column1)
        if a is None :
            return True
        else:
            return False