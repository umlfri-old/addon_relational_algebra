class Tabulka:
    def __init__(self,nazov,data,pravy=None,lavy=None):
        self.__name=nazov
        self.__right=pravy
        self.__left=lavy
        self.__database=data
    def execute(self):
        self.__database.dajData(self.__name)

class Difference:
    def __init__(self,lavy=None,pravy=None):
        self.__left=lavy
        self.__right=pravy
    def execute(self):
        self.__left.execute()
        self.__right.execute()

