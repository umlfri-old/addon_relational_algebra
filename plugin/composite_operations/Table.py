__author__ = 'Michal'


class Table:
    def __init__(self, connection, table):
        self.__table = table
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
