__author__ = 'Michal'

from relation import Relation
from error import CompileError


class Intersection:
    def __init__(self):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__name = "Intersection"
        self.__element = None
        self.__data = None
        self.__position = None

    def set(self, ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left = ancestor
        else:
            self.__ancestor_right = ancestor

    def get_position(self):
        return self.__position

    def move(self, cords):
        self.__ancestor_left.move(cords)
        self.__ancestor_right.move(cords)
        self.__element.move(cords[self.__position])

    def paint(self, interface, diagram, graph):
        connection_left = interface.project.metamodel.connections["Relationship"]
        connection_right = interface.project.metamodel.connections["Relationship"]
        ancestor_element_left, left_position = self.__ancestor_left.paint(interface, diagram, graph)
        ancestor_element_right, right_position = self.__ancestor_right.paint(interface, diagram, graph)
        el = self.create_element(interface, diagram)
        self.__position = len(graph.vs)
        graph.add_vertex(self.__element.object.values['name'])
        graph.add_edge(left_position, self.__position)
        graph.add_edge(right_position, self.__position)
        ancestor_element_left.connect_with(el, connection_left)
        ancestor_element_right.connect_with(el, connection_right)
        return el, self.__position

    def create_element(self, interface, diagram):
        if self.__element is None:
            element = interface.project.metamodel.elements[self.__name]
            el = diagram.create_element(element)
            self.__element = el
        return self.__element

    def execute(self):
        if self.__data is None:
            left_data = self.__ancestor_left.execute()
            right_data = self.__ancestor_right.execute()
            left_data.intersection(right_data)
            self.__data = left_data
            return self.__data
        else:
            return self.__data