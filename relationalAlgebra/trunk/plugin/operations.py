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

        #vytvori novy header so stlpcami, ktore selectujeme
        for i in range(len(header[0])-1,-1,-1):
            try:
                indexes.index(i)
            except ValueError:
                del header[0][i]
                del header[1][i]
        relation=Relation(header)
        #upravi kazdy riadok(vymaze stlpce ktore sme neselectovali)
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
        #zisti ci podmienka je cislo ak nie je odstrani prvu a poslednu uvodzovku a vytvori novy string
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
        #zisti ci sa ziadany stlpec nachadza v danej relacii
        try:
            index=header[0].index(self.__column)
        except ValueError:
            try:
                index=header[1].index(self.__column)
            except ValueError:
                print "selection error"
                return None
        relation=Relation(header)
        #prejde vsetkymi riadkami relacie a zisti ci vyhovuje podmienke
        #ak ano tak riadok prida do novej relacie
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
        #hlavicky oboch relacii spoji do novej hlavicky
        header_new[0]=header[0]+header1[0]
        header_new[1]=header1[1]+header1[1]
        relation=Relation(header_new)
        #prejde vsetkymi riadkami relacie a skombinuje ich s riadkami relacie1 a prida do novej relacie
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
        relation=Relation(header)
        #ak sa relacie rovnaju tak prejde vsetkymi riadkami relacie a prida ich do novej a potom prejde vsetkymi
        #riadkami relacie1 a prida ich do novej
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
        #ak sa hlavicky oboch relacii rovnaju tak prejde vsetkymi riadkami relacie a zisti ci sa data nachadzaju
        #aj v relacii1 ak ano tak riadok prida do novej relacie
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
        columns=ret.getHeader()
        columns_help=copy.deepcopy(columns)
        columns1=ret1.getHeader()
        indexes=[]
        indexes2=[]
        match={}
        #ulozi do premennej indexes cisla stlpcov, ktore treba delit
        for i in range(0,len(columns1[0])):
            try:
                indexes.append(columns[0].index(columns1[0][i]))
                columns[0].remove(columns1[0][i])
                del columns[1][indexes[-1]]
            except ValueError:
                print "division error"
                return None
        relation=Relation(columns)
        #ulozi do premennej indexes2 cisla stlpcov, ktore ostanu vo vyslednej relacii
        for i in range(0,len(columns[0])):
            indexes2.append(columns_help[0].index(columns[0][i]))
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
                relation.addRow(Row(row,copy.deepcopy(columns)))
        return relation
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
        #zisti ci sa hlavicky rovnaju v oboch relaciach
        if header[0]==header1[0]:
            #pre kazdy riadok relacie skusi najst zaznam v druhej relacii ak nenajde tak zaznam prida do novej relacie
            for i in ret:
                try:
                    ret1.getData().index(i.getData())
                except ValueError:
                    relation.addRow(Row(i.getData(),i.getHeader()))
        else:
            print "difference error"
            return None
        return relation
class Join:
    def __init__(self,column1,condition,column2,left=False,right=False):
        self.__ancestor_left=None
        self.__ancestor_right=None
        self.__column1=column1
        self.__condition=condition
        self.__column2=column2
        self.__right=right
        self.__left=left
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
        indexes1,indexes2=find(header,header1,self.__column1,self.__column2)
        #skontroluje ci sa obidve stlpce nachadzaju v tabulkach a ci sa nachadzaju prave len raz
        if len(indexes1)+len(indexes2) != 2:
            print "inner join error"
            return None
        if len(indexes1) is 2:
            #obidva stlpce su z druhej tabulky
            print "inner join error"
            return None
        elif len(indexes2) is 2:
            #obidva stlpce su z druhej tabulky
            print "inner join error"
            return None
        else:
            #jeden stlpec z jednej tabulky, druhy stlpec z druhej tabulky
            used=set()
            new_columns=[[],[]]
            new_columns[0]=header[0]+header1[0]
            new_columns[1]=header[1]+header1[1]
            relation=Relation(new_columns)
            for i in ret:
                number=0
                for y in ret1:
                    if condition(i.getData(indexes1[0]),y.getData(indexes2[0]),self.__condition):
                        new=i.getData()+y.getData()
                        relation.addRow(Row(new,copy.deepcopy(new_columns)))
                        number +=1
                        if self.__right:
                            used.add(y.getString())
                if number is 0 and self.__left:
                    new1=[]
                    for row in range(0,len(header1[0])):
                        new1.append("")
                    new=i.getData()+new1
                    relation.addRow(Row(new,copy.deepcopy(new_columns)))
            if self.__right:
                for y in ret1:
                    string=y.getString()
                    if string not in used:
                        new1=[]
                        for row in range(0,len(header[0])):
                            new1.append("")
                        new=new1+y.getData()
                        relation.addRow(Row(new,copy.deepcopy(new_columns)))
        return relation
def condition(column1,column2,condition):
    if condition=="=" :
        if column1 == column2:
            return True
        else :
            return False
    elif condition=="<":
        if column1 < column2:
            return True
        else :
            return False
    elif condition==">":
        if column1 > column2:
            return True
        else :
            return False
    elif condition==">=":
        if column1 >= column2:
            return True
        else :
            return False
    elif condition=="<=":
        if column1 <= column2:
            return True
        else :
            return False
    elif condition=="!=":
        if column1 != column2:
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
def find(header1,header2,column1,column2):
    indexes1=[]
    indexes2=[]
    try:
        indexes1.append(header1[0].index(column1))
    except ValueError:
        pass
    try:
        indexes1.append(header1[1].index(column1))
    except ValueError:
        pass
    try:
        indexes1.append(header1[0].index(column2))
    except ValueError:
        pass
    try:
        indexes1.append(header1[1].index(column2))
    except ValueError:
        pass
    try:
        indexes2.append(header2[0].index(column1))
    except ValueError:
        pass
    try:
        indexes2.append(header2[1].index(column1))
    except ValueError:
        pass
    try:
        indexes2.append(header2[0].index(column2))
    except ValueError:
        pass
    try:
        indexes2.append(header2[1].index(column2))
    except ValueError:
        pass
    return indexes1,indexes2