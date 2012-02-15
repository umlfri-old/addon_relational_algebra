class Tabulka:
    def __init__(self,data,table):
        self.__database=data
        self.__table_name=table

    def execute(self):
        return self.__database.dajData(self.__table_name)

class Projection:
    def __init__(self,data):
        self.__data=data
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        self.__ancestor.execute()
class Selection:
    def __init__(self,column,condition,data):
        self.__column=column
        self.__condition=condition
        self.__data=data
    def set(self,ancestor):
        self.__ancestor=ancestor
    def execute(self):
        self.__ancestor.execute()