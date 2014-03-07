__author__ = 'Michal'


class Join:
    def __init__(self, left=False, right=False):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__right = right
        self.__left = left
        self.__condition = None

    def set(self, ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left = ancestor
        else:
            self.__ancestor_right = ancestor

    def set_condition(self, condition):
        self.__condition = condition