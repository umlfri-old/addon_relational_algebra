__author__ = 'Michal'

from error import CompileError
import copy
import sqlparse
import ast


class Projection:
    def __init__(self, columns, i=False):
        if not i:
            self.__columns = []
            columns = ast.literal_eval(columns)
            for column in columns:
                self.__columns.append(sqlparse.parse(column["meno"])[0].token_first())
        else:
            self.__columns = columns
        self.__ancestor = None
        self.__name = "Projection"
        self.__element = None
        self.__data = None
        self.__position = None

    def get_position(self):
        return self.__position

    def move(self, cords):
        self.__ancestor.move(cords)
        self.__element.move(cords[self.__position])

    def set(self,ancestor):
        self.__ancestor = ancestor

    def paint(self, interface, diagram, graph, level):
        connection = interface.project.metamodel.connections["Relationship"]
        ancestor_element, position, ancestor_level = self.__ancestor.paint(interface, diagram, graph, level)
        el = self.create_element(interface, diagram)
        self.__position = len(graph.vs)
        graph.add_vertex(self.__element.object.values['name'])
        graph.add_edge(position, self.__position)
        ancestor_element.connect_with(el, connection)
        level = ancestor_level + 1
        return el, self.__position, level

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