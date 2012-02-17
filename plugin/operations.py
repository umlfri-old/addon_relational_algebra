class Table:
    def __init__(self,data,table):
        self.__database=data
        self.__table_name=table

    def execute(self):
        return 1
        #return self.__database.dajData(self.__table_name)
    def __str__(self):
        return "ja som table s menom" + self.__table_name
class Projection:
    def __init__(self,data):
        self.__data=data
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        ret=self.__ancestor.execute()
        return ret+1
    def __str__(self):
        ret=self.__ancestor.__str__()
        return ret+"..."+"ja som projection "
class Selection:
    def __init__(self,column,condition,data):
        self.__column=column
        self.__condition=condition
        self.__data=data
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        ret=self.__ancestor.execute()
        return ret+2
    def __str__(self):
        ret=self.__ancestor.__str__()
        return ret+"..."+"ja som select"
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
        return ret*ret1
    def __str__(self):
        ret=self.__ancestor_left.__str__()
        ret1=self.__ancestor_right.__str__()
        return ret+ret1+"..."+"ja som union"
