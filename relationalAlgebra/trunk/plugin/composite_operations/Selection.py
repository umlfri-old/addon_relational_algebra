__author__ = 'Michal'


import sqlparse

from sqlparse import sql as Objects
from error import CompileError


class Selection:
    def __init__(self, left_operand, operation, right_operand, diagram=True):
        if not diagram:
            self.__left_operand = sqlparse.parse(left_operand)[0].token_first()
        else:
            self.__left_operand = left_operand

        if not diagram and not operation in("NOT IN", "IN"):
            self.__right_operand = sqlparse.parse(right_operand)[0].token_first()
        else:
            if operation in ("NOT IN", "IN"):
                self.__right_operand = right_operand.__str__()
                if self.__right_operand[0] != "(" and self.__right_operand[-1] != ")":
                    raise CompileError("Except list of values", "Selection error")
            else:
                self.__right_operand = right_operand

        if operation.__str__() == "<>":
            self.__operation = "!="
        else:
            self.__operation = operation

        self.__ancestor = None
        self.__name = "Selection"
        self.__element = None
        self.__data = None

    def set(self, ancestor):
        self.__ancestor = ancestor

    def paint(self, interface, diagram):
        connection = interface.project.metamodel.connections["Relationship"]
        ancestor_element = self.__ancestor.paint(interface, diagram)
        el = self.create_element(interface, diagram)
        ancestor_element.connect_with(el, connection)
        return el

    def create_element(self, interface, diagram):
        if self.__element is None:
            element = interface.project.metamodel.elements[self.__name]
            el = diagram.create_element(element)
            el.object.values['column1'] = self.__left_operand.__str__()
            el.object.values['condition'] = self.__operation.__str__()
            el.object.values['column2'] = self.__right_operand.__str__()
            self.__element = el
        return self.__element

    def execute(self):
        if self.__data is None:
            left_data = self.__ancestor.execute()
            left_data.selection(self.__left_operand, self.__operation, self.__right_operand)
            self.__data = left_data
            return self.__data
        else:
            return self.__data