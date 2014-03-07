__author__ = 'Michal'


class Table:
    def __init__(self, table):
        self.__table = table
        self.__name = "Table"

    def paint(self, interface, diagram):
        element = interface.project.metamodel.elements[self.__name]
        diagram.create_element(element)