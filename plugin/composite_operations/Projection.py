__author__ = 'Michal'

from error import CompileError
import copy
import sqlparse

class Projection:
    def __init__(self, columns, i=False):
        if not i:
            self.__columns = []
            a = columns.rsplit(":")
            for i in range(1, len(a)):
                b = a[i].rsplit("'")
                column = sqlparse.parse((b[1].lower()))
                self.__columns.append(column[0].token_first())
        else:
            self.__columns = columns
        self.__ancestor = None
        self.__name = "Projection"
        self.__element = None
        self.__data = None

    def set(self,ancestor):
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
            columns = []
            for column in self.__columns:
                c = {}
                c['meno'] = column.__str__()
                columns.append(c)
            el.object.values['c'] = columns
            self.__element = el
        return self.__element

    def execute(self):
        if self.__data is None:
            relation = self.__ancestor.execute()
            relation.projection(self.__columns)
            self.__data = relation
            return self.__data
        else:
            return self.__data