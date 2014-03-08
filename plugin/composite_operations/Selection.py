__author__ = 'Michal'


class Selection:
    def __init__(self, left_operand, operation, right_operand):
        self.__left_operand = left_operand
        self.__right_operand = right_operand
        self.__operation = operation
        self.__ancestor = None
        self.__name = "Selection"
        self.__element = None

    def set(self, ancestor):
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
            el.object.values['column1'] = self.__left_operand.__str__()
            el.object.values['condition'] = self.__operation.__str__()
            el.object.values['column2'] = self.__right_operand.__str__()
            self.__element = el
        return self.__element

