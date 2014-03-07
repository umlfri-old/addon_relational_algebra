__author__ = 'Michal'
class Projection:
    def __init__(self, data):
        self.__data = data
        self.__ancestor = None
    def set(self,ancestor):
        self.__ancestor = ancestor