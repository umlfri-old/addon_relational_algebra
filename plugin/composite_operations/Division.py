__author__ = 'Michal'

from Product import Product
from Projection import Projection
from Difference import Difference
import copy
from error import CompileError
from relation import Relation

class Division:
    def __init__(self):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__name = "Division"
        self.__element = None
        self.__data = None
        self.__position = (0, 0)

    def set(self,ancestor):
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
            try:
                d_headers = left_data.difference_headers(right_data)
                left_data_orig = copy.deepcopy(left_data)
                t = left_data_orig.projection(d_headers).product(right_data)
                a = t.difference(left_data).projection(d_headers)
                left_data.projection(d_headers).difference(a)
            except CompileError:
                raise CompileError("Division error", "Division error")
            self.__data = left_data
            return self.__data
        else:
            return self.__data


