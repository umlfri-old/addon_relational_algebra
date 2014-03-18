__author__ = 'Michal'

from error import CompileError
import copy


class Projection:
    def __init__(self, data):
        self.__data = []
        a = data.rsplit(":")
        for i in range(1, len(a)):
            b = a[i].rsplit("'")
            self.__data.append(b[1].lower())
        self.__ancestor = None
        self.__name = "Projection"
        self.__element = None

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
            for column in self.__data:
                c = {}
                c['meno'] = column.__str__()
                columns.append(c)
            el.object.values['c'] = columns
            self.__element = el
        return self.__element

    def execute(self):
        relation = self.__ancestor.execute()
        columns = copy.deepcopy(relation.getHeader())
        for column in self.__data:
            try:
                relation.getHeader().index(column)
            except ValueError:
                raise CompileError(column+" not found in table", "Projection error in "+self.__name)

        for column in columns:
            if column not in self.__data:
                relation.removeColumn(column)

        return relation