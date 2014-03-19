__author__ = 'Michal'

from error import CompileError
from relation import *

class Table:
    def __init__(self, connection, table):
        self.__table = table
        if table == "":
            raise CompileError("Table error. You must type name of table", "Compile error")
        self.__name = "Table"
        self.__element = None
        self.__connection = connection

    def paint(self, interface, diagram):
        return self.create_element(interface, diagram)

    def create_element(self, interface, diagram):
        if self.__element is None:
            element = interface.project.metamodel.elements[self.__name]
            el = diagram.create_element(element)
            el.object.values['table_name'] = self.__table
            self.__element = el
        return self.__element

    def execute(self):
        try:
            header = self.__connection.getColumns(self.__table)
            relation = Relation(header, self.__table)
        except CompileError as e:
            raise CompileError(e.getValue(),e.getName())


        try:
            data = self.__connection.getData(self.__table)
        except CompileError as e:
            raise CompileError(e.getValue(), e.getName())


        for i in range(0, len(data)):
            new = []
            for y in range(0, len(data[i])):
                new.append(data[i][y])
            relation.addRow(new)
        unique_relation = Relation(relation.getHeader(), relation.getName())
        [unique_relation.addRow(list(x)) for x in set(tuple(x) for x in relation)]
        return unique_relation