class Table:
    def __init__(self,data,table):
        self.__database=data
        self.__table_name=table
    def execute(self):
        cursor=self.__database.vykonaj('SHOW COLUMNS IN ' +self.__table_name)
        columns=[]
        i=0
        for row in cursor:
            for column in row:
                if i==0:
                    columns.append(column)
                i=i+1
            i=0
        data=self.__database.dajData(self.__table_name)
        table=[]
        tem=list(data)
        for i in range(0,len(tem)):
            if(i==0):
                table.append(columns)
            new=[]
            for y in range(0,len(columns)):
                new.append(tem[i][y])
            table.append(new)
        return table
class Projection:
    def __init__(self,data):
        self.__data=[]
        a=[]
        b=[]
        a=data.rsplit(":")
        for i in range(1,len(a)):
            b=a[i].rsplit("'")
            self.__data.append(b[1])
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        ret=self.__ancestor.execute()
        columns=ret[0]
        indexes=[]
        table=[]
        for i in range(0,len(self.__data)):
            try:
                indexes.append(columns.index(self.__data[i]))
            except ValueError:
                pass
        for i in range(0,len(ret)):
            new=[]
            for y in range(0,len(columns)):
                try:
                    a=indexes.index(y)
                    new.append(ret[i][y])
                except ValueError:
                    pass
            table.append(new)
        return table
class Selection:
    def __init__(self,column,condition,data):
        self.__column=column
        self.__condition=condition
        self.__data=data
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        ret=self.__ancestor.execute()
        columns=ret[0]
        try:
            index=columns.index(self.__column)
        except ValueError:
            return None
        table=[]
        for i in range(0,len(ret)):
            new=[]
            for y in range(0,len(columns)):
                try:
                    if(ret[i][index]):
                        pass
                except ValueError:
                    pass
            table.append(new)
class Product:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if(self.__ancestor_left==None):
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        table=[]
        columns=ret[0]+ret1[0]
        table.append(columns)
        for i in range(1,len(ret)):
            for y in range(1,len(ret1)):
                new=ret[i]+ret1[y]
                table.append(new)
        return table
class Union:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if(self.__ancestor_left==None):
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        columns=ret[0]
        columns1=ret1[0]
        table=[]
        if columns==columns1:
            table.append(columns)
            for i in range(1,len(ret)):
                table.append(ret[i])
            for i in range(1,len(ret1)):
                table.append(ret1[i])
        else:
            print "union incompatible error"
            return None
        return table
class Intersection:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if(self.__ancestor_left==None):
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        columns=ret[0]
        columns1=ret1[0]
        table=[]
        if columns==columns1:
           table.append(columns)
           for i in range(1,len(ret)):
               try:
                   ret1.index(ret[i])
                   table.append(ret[i])
               except ValueError:
                   pass
        else:
            print "intersection incompatible error"
            return None
        return table
class Division:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if(self.__ancestor_left==None):
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        columns=ret[0]
        columns1=ret1[0]
        print columns
        print columns1
        table=[]
        indexes=[]
        for i in range(0,len(columns1)):
            try:
                indexes.append(columns.index(columns1[i]))
                columns.remove(columns1[i])
            except ValueError:
                print "division error"
                return None
        table.append(columns)
        return table
class Difference:
    def __init__(self):
        self.__ancestor_left=None
        self.__ancestor_right=None
    def set(self,ancestor):
        if(self.__ancestor_left==None):
            self.__ancestor_left=ancestor
        else:
            self.__ancestor_right=ancestor
    def execute(self):
        ret=self.__ancestor_left.execute()
        ret1=self.__ancestor_right.execute()
        columns=ret[0]
        columns1=ret1[0]
        print columns
        print columns1
        table=[]
        table.append(columns)
        if columns==columns1:
            for i in range(1,len(ret)):
                try:
                    ret1.index(ret[i])
                except ValueError:
                    table.append(ret[i])
        else:
            print "difference error"
            return None
        return table