import re
import copy
from relation import *
from row import *
from error import *
from MySQLdb import ProgrammingError
import psycopg2
import datetime
import time
from datetime import timedelta
import math

class Interval():
    def __init__(self,years,months,precision):
        self.__years=years
        self.__months=months
        self.__precision=precision
        if str(self.__years)[0]=="-":
            self.__sign="-"
        else:
            self.__sign="+"
    def getSign(self):
        return self.__sign

    def getYears(self):
        return self.__years
    def getMonths(self):
        return self.__months
    def __str__(self):
        spaceMonths=""
        spaceYears=""
        if self.__months<10:
            spaceMonths += "0"
        if len(str(self.__years))!=self.__precision:
             for i in range(0,self.__precision-1):
                 spaceYears +="0"
        return self.__sign+spaceYears+str(int(math.fabs(self.__years)))+"-"+spaceMonths+str(self.__months)

    def __cmp__(self, other):
        months=int(math.fabs(self.getYears()))*12+self.getMonths()
        monthsOther=int(math.fabs(other.getYears()))*12+other.getMonths()
        if months == monthsOther and self.getSign()==other.getSign():
            return 0
        elif months<monthsOther and self.getSign()==other.getSign():
            return -1
        elif months>monthsOther and self.getSign()==other.getSign():
            return 1
        elif self.getSign()!=other.getSign():
            if self.getSign()=="+":
                return 1
            else:
                return -1
class Table:
    def __init__(self,data,table):
        self.__database=data
        self.__table_name=table.lower()
        if table=="":
            raise CompileError("Table error. You must type name of table","Compile error")
    def execute(self):
        #return name of columns and store into variable header
        try:
            header=self.__database.getColumns(self.__table_name)
        except CompileError as e:
            raise CompileError(e.getValue(),e.getName())
        except ProgrammingError as e:
            raise CompileError(e.__str__(),"Compile error")
        except psycopg2.ProgrammingError as e:
            raise CompileError(e.__str__(),"CompileError")
        table_name=[self.__table_name]
        #create new relation with columns name
        relation=Relation(header,self.__table_name)
        #return data from table
        try:
            data=self.__database.getData(self.__table_name)
        except CompileError as e:
            raise CompileError(e.getValue(),e.getName())
        except ProgrammingError as e:
            raise CompileError(e.__str__(),"Compile error")
        except psycopg2.ProgrammingError as e:
            raise CompileError(e.__str__(),"CompileError")
        tem=list(data)
        #for row in tem:
        #    for column in row:
        #        print type(column)
        #        print column
        #from all data create class row with columns name(columns name with their table name) and with data and add to relation
        for i in range(0,len(tem)):
            new=[]
            for y in range(0,len(tem[i])):
                new.append(tem[i][y])
            header1=copy.deepcopy(header)
            relation.addRow(Row(new))
        return relation
class Projection:
    def __init__(self,name,data):
        #attribute to store name of columns,which are selected from relation
        self.__data=[]
        if data=="":
            raise CompileError("Projection error in "+ name+". You must enter names of columns, which you want select","Compile error")
        self.__name=name
        a=data.rsplit(":")
        for i in range(1,len(a)):
            b=a[i].rsplit("'")
            self.__data.append(b[1].lower())
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
                index=findElement(header,self.__data[i])
                indexes.append(index)
            except ValueError:
                raise CompileError(self.__data[i]+" not found in table","Projection error in "+self.__name)
        #vytvori novy header so stlpcami, ktore selectujeme
        for i in range(len(header)-1,-1,-1):
            try:
                indexes.index(i)
            except ValueError:
                del header[i]
        relation=Relation(header,self.__name)
        #upravi kazdy riadok(vymaze stlpce ktore sme neselectovali)
        for row in ret:
            for i in range(row.getLen()-1,-1,-1):
                try:
                    indexes.index(i)
                except ValueError:
                    row.deleteColumn(i)
            relation.addRow(row)
        return relation
def findElement(array,data):
    for i in range(0,len(array)):
        try:
            index=array[i].index(data)
            return i
        except ValueError:
            pass
    raise ValueError
class Selection:
    def __init__(self,name,column,condition,data):
        if column=="":
            raise CompileError("Selection error in "+ name+". You must enter names of columns1","Compile error")
        self.__column=column
        self.__name=name
        if condition==" ":
            raise CompileError("Selection error in "+ name+". You must enter condition, which you want select","Compile error")
        self.__condition=condition
        if data=="":
            raise CompileError("Selection error in "+ name+". You must enter names of columns2","Compile error")
        if condition=="IS" or condition == "IS NOT":
            if data!="NULL" and column!="NULL":
                raise CompileError("Selection error in "+ name+". If condition is '"+condition+"', You must compare with NULL value","Compile error")
        self.__data=data
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        ret=self.__ancestor.execute()
        header=ret.getHeader()
        relation=Relation(header,self.__name)
        index=[]
        index1=check(self.__column,header,self.__name,self.__condition)
        index2=check(self.__data,header,self.__name,self.__condition)
        if self.__condition == "LIKE" or self.__condition=="NOT LIKE":
            if type(index1) is not str and type(index2) is not str:
                raise CompileError("Condition 'LIKE' and 'NOT LIKE' can be use only with string","Selection error in "+self.__name)
        self.__column="~"
        self.__data="~"
        if type(index1) is str or type(index1) is float or index1 is None or type(index1) is datetime.date or type(index1) is datetime.datetime or type(index1) is datetime.timedelta or isinstance(index1,Interval) :
            self.__column=index1
        elif type(index1) is int:
            index.append(index1)
        if type(index2) is str or type(index2) is float or index2 is None or type(index2) is datetime.date or type(index2) is datetime.datetime or type(index2) is datetime.timedelta or isinstance(index2,Interval):
            self.__data=index2
        elif type(index2) is int:
            index.append(index2)
        #prejde vsetkymi riadkami relacie a zisti ci vyhovuje podmienke
        #ak ano tak riadok prida do novej relacie
        if len(index)==2:
            for i in ret:
                if condition(i.getData(index[0]),i.getData(index[1]),0,self.__condition,self.__name):
                    relation.addRow(Row(i.getData()))
            return relation
        elif len(index)==1 and self.__column=="~":
            for i in ret:
                if condition(i.getData(index[0]),self.__data,1,self.__condition,self.__name):
                    relation.addRow(Row(i.getData()))
            return relation
        elif len(index)==1 and self.__data=="~":
            for i in ret:
                if condition(self.__column,i.getData(index[0]),2,self.__condition,self.__name):
                    relation.addRow(Row(i.getData()))
            return relation
        else:
            for i in ret:
                if condition(self.__column,self.__data,0,self.__condition,self.__name):
                    relation.addRow(Row(i.getData()))
            return relation
def check(column,header,name,condition1):
    #zisti ci stlpec je string, cislo alebo odkaz na stlpec
    if(column[0]=='"') and (column[-1]=='"') or (column[0]=="'" and column[-1]=="'"):
        column1=""
        for i in range(0,len(column)):
            if (i!=0)&(i!=(len(column)-1)):
                column1=column1+column[i]
        if len(column1) is 0:
            raise CompileError("Column name cannot be empty string","Selection error in "+name)
        return column1
    elif column=="NULL":
        if condition1=="IS" or condition1=="IS NOT":
            column1=None
            return column1
        else:
            raise CompileError("Column name cannot be 'NULL' without 'IS' or 'IS NOT' condition","Selection error in "+name)
    else:
        try:
            index=findElement(header,column.lower())
        except ValueError:
            try:
                index=float(column)
            except ValueError:
                if condition1!="LIKE" or condition1!="NOT LIKE" or condition1!="IS" or condition1!="IS NOT":
                    try:
                        time_format = "%Y-%m-%d %H:%M:%S"
                        index=datetime.datetime.fromtimestamp(time.mktime(time.strptime(column, time_format)))
                        return index
                    except ValueError:
                        try:
                            time_format = "%Y-%m-%d"
                            index=datetime.date.fromtimestamp(time.mktime(time.strptime(column, time_format)))
                            return index
                        except ValueError:
                            try:
                                index=parse_time(column)
                                return index
                            except ValueError:
                                try:
                                    index=parse_time1(column)
                                    return index
                                except ValueError:
                                    raise CompileError(column+ " is not valid. Value without quotes can be use only with number, date(YYYY-MM-DD HH:MM:SS or YYYY-MM-DD) or interval(D HH:MM:SS)","Selection error in "+name)
                else:
                    if condition1=="IS" or condition1=="IS NOT":
                        raise CompileError("Condition  'IS' and 'IS NOT' can be compare only with 'NULL'","Selection error in "+name)
                    elif condition1=="LIKE" or condition1=="NOT LIKE":
                        raise CompileError("Condition 'LIKE' and 'NOT LIKE' can be compare only with string","Selection error in "+name )
        return index
class Product:
    def __init__(self,name):
        self.__name=name
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
        header_new=[]
        #hlavicky oboch relacii spoji do novej hlavicky
        header_new=header+header1
        relation=Relation(header_new,self.__name)
        #prejde vsetkymi riadkami relacie a skombinuje ich s riadkami relacie1 a prida do novej relacie
        for i in ret:
            for y in ret1:
                new=i.getData()+y.getData()
                relation.addRow(Row(new))
        return relation
class Union:
    def __init__(self,name):
        self.__name=name
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
        columnsName=ret.getColumnsName()
        columnsName1=ret1.getColumnsName()
        header=ret.getHeader()
        header1=ret1.getHeader()
        for head in header:
            while len(head)!=1:
                del head[-1]
        relation=Relation(header,self.__name)
        #ak sa relacie rovnaju tak prejde vsetkymi riadkami relacie a prida ich do novej a potom prejde vsetkymi
        #riadkami relacie1 a prida ich do novej
        if columnsName==columnsName1:
            for i in ret:
                relation.addRow(Row(i.getData()))
            for i in ret1:
                relation.addRow(Row(i.getData()))
        else:
            raise CompileError("Columns`s names in tables are different","Union error in"+self.__name)
        return relation
class Intersection:
    def __init__(self,name):
        self.__name=name
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
        columnsName=ret.getColumnsName()
        columnsName1=ret1.getColumnsName()
        header=ret.getHeader()
        header1=ret1.getHeader()
        for head in header:
            while len(head)!=1:
                del head[-1]
        relation=Relation(header,self.__name)
        #ak sa hlavicky oboch relacii rovnaju tak prejde vsetkymi riadkami relacie a zisti ci sa data nachadzaju
        #aj v relacii1 ak ano tak riadok prida do novej relacie
        if columnsName==columnsName1:
           for i in ret:
               try:
                   ret1.getData().index(i.getData())
                   relation.addRow(Row(i.getData()))
               except ValueError:
                   pass
        else:
            raise CompileError("Columns`s names in tables are different","Intersection error in "+self.__name)
        return relation
class Division:
    def __init__(self,name):
        self.__name=name
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
        columns=ret.getHeader()
        columns_help=copy.deepcopy(columns)
        columns1=ret1.getHeader()
        indexes=[]
        indexes2=[]
        match={}
        #ulozi do premennej indexes cisla stlpcov, ktore treba delit
        for i in range(0,len(columns1)):
            try:
                indexes.append(findElement(columns,columns1[i][0]))
                del columns[indexes[-1]]
            except ValueError:
                raise CompileError("Columns`s names are not founded in table","Division error in "+self.__name)
        relation=Relation(columns,self.__name)
        #ulozi do premennej indexes2 cisla stlpcov, ktore ostanu vo vyslednej relacii
        for i in range(0,len(columns)):
            indexes2.append(findElement(columns_help,columns[i][0]))
        #pre vsetky riadky v relacii zostavy string zo stlpcov, ktorymi delime, a ulozi do premennej match novy zaznam
        #ak este zaznam neexistuje v premmenej matches alebo zvysi pocet najdenych zaznamov o jedna ak sa tam uz nachadza
        for i in ret :
            string1=""
            for a in range(0,len(indexes)):
                string1=string1+","+ i.getData(indexes[a])
            for y in ret1:
                string2=""
                for b in range(0,len(indexes)):
                    string2=string2+","+y.getData(b)
                if string1==string2:
                    string3=""
                    for c in range(0,len(indexes2)):
                        string3=string3+","+i.getData(indexes2[c]).__str__()
                    if match.get(string3) is None :
                        new= [string3, 1]
                        match[string3]=new
                    else:
                        new=match.get(string3)
                        number=new[1]
                        new[1]=number+1
                        match[string3]=new
        #vyberie vsetky hodnoty
        values=match.values()
        #pre vsetky hodnoty skontroluje, ktorej hodnoty sa pocet rovna poctu riadkov, ktorymi sme delili
        #pre tu ktora vyhovuje rozdeli jej hodnotu podla ciarky na stlpce a vytvori novy Row s tymito hodnotami a nasledne
        #prida do relacie
        for i in range(0,len(values)):
            new=values[i]
            if new[1]== ret1.getLen():
                row=new[0]
                new1=row.rsplit(",")
                row=[]
                for y in range(0,len(new1)):
                    if y is not 0:
                        row.append(new1[y])
                relation.addRow(Row(row))
        return relation
class Difference:
    def __init__(self,name):
        self.__name=name
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
        columnsName=ret.getColumnsName()
        columnsName1=ret1.getColumnsName()
        header=ret.getHeader()
        header1=ret1.getHeader()
        relation=Relation(header,self.__name)
        #zisti ci sa hlavicky rovnaju v oboch relaciach
        if columnsName==columnsName1:
            #pre kazdy riadok relacie skusi najst zaznam v druhej relacii ak nenajde tak zaznam prida do novej relacie
            for i in ret:
                try:
                    ret1.getData().index(i.getData())
                except ValueError:
                    relation.addRow(Row(i.getData()))
        else:
            raise CompileError("Columns`s names in tables are different","Difference error in "+self.__name)
        return relation
class Join:
    def __init__(self,name,column1,condition,column2,left=False,right=False):
        self.__name=name
        if column1=="" and column2=="" and condition==" ":
            self.__natural=True
        else:
            self.__natural=False
        self.__ancestor_left=None
        self.__ancestor_right=None
        self.__column1=column1
        self.__condition=condition
        self.__column2=column2
        self.__right=right
        self.__left=left
        if right:
            self.__type="Right outter join"
        elif left:
            self.__type="Left outter join"
        elif right and left:
            self.__type="Full outter join"
        elif self.__natural:
            self.__type="Natural join"
            self.__condition="="
        else:
            self.__type="Inner join"
        if not self.__natural and column1=="":
            raise CompileError(self.__type+" error in "+ name+". You must enter names of columns1","Compile error")
        if not self.__natural and condition==" ":
            raise CompileError(self.__type+" error in "+ name+". You must enter condition","Compile error")
        if not self.__natural and column2=="":
            raise CompileError(self.__type+" error in "+ name+". You must enter names of columns2","Compile error")
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
        indexes1=[]
        indexes2=[]
        opo=False
        if not self.__natural:
            try:
                findElement(header,self.__column1.lower())
            except ValueError:
                opo=True
            new_columns=header+header1
        try:
            indexes1.append(findElement(header,self.__column1.lower()))
        except ValueError:
            pass
        try:
            indexes1.append(findElement(header,self.__column2.lower()))
        except ValueError:
            pass
        try:
            indexes2.append(findElement(header1,self.__column1.lower()))
        except ValueError:
            pass
        try:
            indexes2.append(findElement(header1,self.__column2.lower()))
        except ValueError:
            pass
        #skontroluje ci sa obidve stlpce nachadzaju v tabulkach a ci sa nachadzaju prave len raz
        if len(indexes1)+len(indexes2)<2 and not self.__natural:
            raise CompileError("Some columns names are wrong",self.__type+" error in "+self.__name)
        if len(indexes1)+len(indexes2) > 2 and not self.__natural:
            raise CompileError("Columns`s names are not unique",self.__type+" error in "+self.__name)
        if len(indexes1) is 2 and not self.__natural:
            #obidva stlpce su z prvej tabulky
            raise CompileError("Both of names are from first table",self.__type+" error in "+self.__name)
        elif len(indexes2) is 2 and not self.__natural:
            #obidva stlpce su z druhej tabulky
            raise CompileError("Both of names are from second table",self.__type+" error in "+self.__name)
        else:
            #jeden stlpec z jednej tabulky, druhy stlpec z druhej tabulky
            used=set()
            if self.__natural:
                for i in range(0,len(header)):
                    try:
                        index=findElement(header1,header[i][0])
                        try:
                            indexes2.index(index)
                            raise CompileError(self.__type + " error in "+ self.__name+". Tables have more columns with same name","Compile error")
                        except ValueError:
                            indexes1.append(i)
                            indexes2.append(index)
                    except ValueError:
                        pass
                new_columns=header
                for index in range(0,len(header1)):
                    try:
                        indexes2.index(index)
                        try:
                            number=findElement(header,header1[index][0])
                            while len(new_columns[number])!=1:
                                del new_columns[number][-1]
                        except ValueError:
                            raise CompileError(self.__type + " error in "+ self.__name,"Compile error")
                    except ValueError:
                        new_columns.append(header1[index])
            if len(indexes1) is 0:
                raise CompileError(self.__type + " error in "+ self.__name+ ". Tables haven`t got any same columns","Compile error")
            relation=Relation(new_columns,self.__name)
            for i in ret:
                number=0
                for y in ret1:
                    previous=True
                    for index in range(0,len(indexes1)):
                        if opo:
                            left=y.getData(indexes2[index])
                            right=i.getData(indexes1[index])
                        else:
                            left=i.getData(indexes1[index])
                            right=y.getData(indexes2[index])
                        if condition(left,right,0,self.__condition,self.__name) and previous:
                            if index is len(indexes1)-1:
                                if not self.__natural:
                                    new=i.getData()+y.getData()
                                else:
                                    new1=[]
                                    for index in range(0,y.getLen()):
                                        try:
                                            indexes2.index(index)
                                        except ValueError:
                                            new1.append(y.getData(index))
                                    new=i.getData()+new1
                                relation.addRow(Row(new))
                                number +=1
                                if self.__right:
                                    used.add(y.getString())
                        else:
                            previous=False
                if number is 0 and self.__left:
                    new1=[]
                    for row in range(0,len(header1)):
                        new1.append("")
                    new=i.getData()+new1
                    relation.addRow(Row(new))
            if self.__right:
                for y in ret1:
                    string=y.getString()
                    if string not in used:
                        new1=[]
                        for row in range(0,len(header)):
                            new1.append("")
                        new=new1+y.getData()
                        relation.addRow(Row(new))
        return relation
def condition(column1,column2,number,condition1,name):
    number=False
    if (column1 is not None and column2 is not None) and (condition1 != "LIKE" and condition1 != "NOT LIKE"):
        if isinstance(column1, (float,int,long,complex)) and isinstance(column2, (float,int,long,complex)):
            number=True
        if type(column1)!=type(column2) and number==False:
            raise CompileError("Types of columns are different","Selection error in "+name)
    if condition1=="=" :
        if column1 == column2:
            return True
        else :
            return False
    elif condition1=="<":
        if column1 < column2:
            return True
        else :
            return False
    elif condition1==">":
        if column1 > column2:
            return True
        else :
            return False
    elif condition1==">=":
        if column1 >= column2:
            return True
        else :
            return False
    elif condition1=="<=":
        if column1 <= column2:
            return True
        else :
            return False
    elif condition1=="!=":
        if column1 != column2:
            return True
        else :
            return False
    elif condition1=="IS":
        if number is 1:
            if column1 is None:
                return True
            else:
                return False
        elif number is 2:
            if column2 is None:
                return True
            else:
                return False
        else:
            return False
    elif condition1 == "IS NOT":
        if number is 1:
            if column1 is not None:
                return True
            else:
                return False
        elif number is 2:
            if column2 is not None:
                return True
            else:
                return False
        else:
            return False
    elif condition1=="LIKE":
        regex=column2.replace(".","\\.\\")
        regex=regex.replace("*","\\*\\")
        regex=regex.replace("_",".")
        regex=regex.replace("%",".*")
        a=re.match(regex,column1.__str__())
        if a is not None :
            return True
        else:
            return False
    elif condition1=="NOT LIKE" :
        regex=column2.replace(".","\\.\\")
        regex=regex.replace("*","\\*\\")
        regex=regex.replace("_",".")
        regex=regex.replace("%",".*")

        a=re.match(regex,column1.__str__())
        if a is None :
            return True
        else:
            return False

def parse_time(time_str):
    regex = re.compile(r'((?P<days>[+-]?\d+\.\d+?|[+-]?\d+?) )((?P<hours>\d+\.\d+?|\d+?):)((?P<minutes>\d+\.\d+?|\d+?):)((?P<seconds>\d+[.]?))?')
    parts = regex.match(time_str)
    if not parts:
        raise ValueError
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            try:
                time_params[name] = int(param)
            except ValueError:
                time_params[name]=float(param)
    if len(time_params) is 0:
        raise ValueError

    return timedelta(**dict(( (key, value)
                              for key, value in time_params.items() )))

def parse_time1(time_str):
    regex = re.compile(r'((?P<years>[+-]?\d+\.\d+?|[+-]?\d+?)-)((?P<months>\d+\.\d+?|\d+[.]?))?')
    parts = regex.match(time_str)
    if not parts:
        raise ValueError
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.iteritems():
        if param:
            try:
                time_params[name] = int(param)
            except ValueError:
                time_params[name] = float(param)
    if len(time_params) is 0:
        raise ValueError
    return Interval(years=time_params['years'],months=time_params['months'],precision=0)

