__author__ = 'Michal'
class Selection:
    def __init__(self, left_operand, operation, right_operand):
        self.__left_operand = left_operand
        self.__right_operand = right_operand
        self.__operation = operation
        self.__ancestor = None

    def set(self, ancestor):
        self.__ancestor = ancestor