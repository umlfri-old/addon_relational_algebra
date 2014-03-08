__author__ = 'Michal'
class Product:
    def __init__(self):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__name = "Product"
        self.__element = None

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
