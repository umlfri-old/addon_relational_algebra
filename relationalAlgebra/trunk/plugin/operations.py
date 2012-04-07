import re
import copy
from relation import *
from row import *
from error import *
from MySQLdb import ProgrammingError
import psycopg2
import datetime,time
import dateutil.parser
from datetime import timedelta

class Table:
    def __init__(self,data,table):
        self.__database=data
        self.__table_name=table
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
        relation=Relation(header,self.__table_name,table_name)
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
            self.__data.append(b[1])
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        #return relation of ancestor
        ret=self.__ancestor.execute()
        #store header
        header=ret.getHeader()
        table_names=ret.getTableNames()
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
        relation=Relation(header,self.__name,table_names)
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
        table_names=ret.getTableNames()
        relation=Relation(header,self.__name,table_names)
        index=[]
        index1=check(self.__column,header,self.__name,self.__condition)
        index2=check(self.__data,header,self.__name,self.__condition)
        if self.__condition == "LIKE" or self.__condition=="NOT LIKE":
            if type(index1) is not str and type(index2) is not str:
                raise CompileError("Condition 'LIKE' and 'NOT LIKE' can be use only with string","Selection error in "+self.__name)
        self.__column="~"
        self.__data="~"
        if type(index1) is str or type(index1) is float or index1 is None or type(index1) is datetime.date or type(index1) is datetime.datetime:
            self.__column=index1
        elif type(index1) is int:
            index.append(index1)
        if type(index2) is str or type(index2) is float or index2 is None or type(index2) is datetime.date or type(index2) is datetime.datetime:
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
            index=findElement(header,column)
        except ValueError:
            try:
                index=float(column)
            except ValueError:
                if condition1!="LIKE" or condition1!="NOT LIKE" or condition1!="IS" or condition1!="IS NOT":
                    try:
                        if ":" in column:
                            try:
                                index = dateutil.parser.parse(column)
                                return index
                            except ValueError:
                                raise CompileError("Format of date is wrong","Selection error in "+name)
                        else:
                            try:
                                index=dateutil.parser.parse(column).date()
                                return index
                            except ValueError:
                                raise CompileError("Format of date is wrong","Selection error in "+name)
                    except Exception:
                        raise CompileError(column+" is not valid","Selection error in "+name)
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
        table_name=ret.getTableNames()
        table_name=table_name+ret.getTableNames()
        #hlavicky oboch relacii spoji do novej hlavicky
        header_new=header+header1
        relation=Relation(header_new,self.__name,table_name)
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
        table_name=ret.getTableNames()+ret1.getTableNames()
        table_name2=ret1.getTableNames()
        for i in range(0,len(header)):
            for y in range(0,len(table_name2)):
                header[i].append(table_name2[y]+"."+header[i][0])
        relation=Relation(header,self.__name,table_name)
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
        table_name=ret.getTableNames()+ret1.getTableNames()
        table_name2=ret1.getTableNames()
        for i in range(0,len(header)):
            for y in range(0,len(table_name2)):
                header[i].append(table_name2[y]+"."+header[i][0])
        relation=Relation(header,self.__name,table_name)
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
        table_name=ret.getTableNames()
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
        relation=Relation(columns,self.__name,table_name)
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
                        string3=string3+","+i.getData(indexes2[c])
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
        table_name=ret.getTableNames()
        relation=Relation(header,self.__name,table_name)
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
                findElement(header,self.__column1)
            except ValueError:
                opo=True
            new_columns=header+header1
            table_name=ret.getTableNames()+ret1.getTableNames()
        try:
            indexes1.append(findElement(header,self.__column1))
        except ValueError:
            pass
        try:
            indexes1.append(findElement(header,self.__column2))
        except ValueError:
            pass
        try:
            indexes2.append(findElement(header1,self.__column1))
        except ValueError:
            pass
        try:
            indexes2.append(findElement(header1,self.__column2))
        except ValueError:
            pass
        #skontroluje ci sa obidve stlpce nachadzaju v tabulkach a ci sa nachadzaju prave len raz
        if len(indexes1)+len(indexes2) != 2 and not self.__natural:
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
                table_name=ret.getTableNames()+ret1.getTableNames()
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
                table_name2=ret1.getTableNames()
                for index in range(0,len(header1)):
                    try:
                        indexes2.index(index)
                        for i in range(0,len(table_name2)):
                            try:
                                number=findElement(header,header1[index][0])

                            except ValueError:
                                raise CompileError(self.__type + " error in "+ self.__name,"Compile error")
                            new_columns[number].append(table_name2[i]+"."+header1[index][0])
                    except ValueError:
                        new_columns.append(header1[index])
            if len(indexes1) is 0:
                raise CompileError(self.__type + " error in "+ self.__name+ ". Tables haven`t got any same columns","Compile error")
            relation=Relation(new_columns,self.__name,table_name)
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
def checkType(column):
    if type(column) is datetime.datetime:
        typ="datetime"
        return typ
    if type(column) is datetime.date:
        typ="date"
        return typ
    if type(column) is str:
        typ="string"
        return typ
    try:
        float(column)
        typ="number"
    except TypeError:
        try:
            str(column)
            typ="string"
        except ValueError:
            typ=column+"unknown"
    return typ
def condition(column1,column2,number,condition1,name):
    if (column1 is not None and column2 is not None) and (condition1 != "LIKE" and condition1 != "NOT LIKE"):
        if type(column1)!=type(column2):
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
    regex = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)hr)?((?P<minutes>\d+?)min)?((?P<seconds>\d+?)s)?((?P<microseconds>\d+?)ms)?')
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    print parts
    time_params = {}
    for (name, param) in parts.iteritems():
        print name
        if param:
            time_params[name] = int(param)

    return timedelta(**dict(( (key, value)
                              for key, value in time_params.items() )))