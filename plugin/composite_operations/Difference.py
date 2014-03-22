__author__ = 'Michal'

from relation import Relation
from error import CompileError

class Difference:
    def __init__(self):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__name = "Difference"
        self.__element = None
        self.__data = None

    def set(self, ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left = ancestor
        else:
            self.__ancestor_right = ancestor

    def paint(self, interface, diagram):
        connection_left = interface.project.metamodel.connections["Relationship"]
        connection_right = interface.project.metamodel.connections["Relationship"]
        ancestor_element_left = self.__ancestor_left.paint(interface, diagram)
        ancestor_element_right = self.__ancestor_right.paint(interface, diagram)
        el = self.create_element(interface, diagram)
        ancestor_element_left.connect_with(el, connection_left)
        ancestor_element_right.connect_with(el, connection_right)
        return el

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
            if left_data.getHeader() == right_data.getHeader():
                relation = Relation(left_data.getHeader(), None)
                for row in left_data.getRows():
                    try:
                        right_data.getRows().index(row)
                    except ValueError:
                        relation.addRow(row)
                unique_relation = Relation(relation.getHeader(), relation.getName())
                [unique_relation.addRow(list(x)) for x in set(tuple(x) for x in relation)]
                self.__data = unique_relation
                return unique_relation
            else:
                raise CompileError("Columns`s names in tables are different", "Union error")
        else:
            return self.__data
