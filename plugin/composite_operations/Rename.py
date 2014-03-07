__author__ = 'Michal'


class Rename:
    def __init__(self, alias,ancestor=None):
        self.__alias = alias
        self.__ancestor = ancestor
    def set(self,ancestor):
        self.__ancestor = ancestor