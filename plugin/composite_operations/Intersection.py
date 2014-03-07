__author__ = 'Michal'


class Intersection:
    def __init__(self):
        self.__ancestor_left = None
        self.__ancestor_right = None
    def set(self, ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left = ancestor
        else:
            self.__ancestor_right = ancestor