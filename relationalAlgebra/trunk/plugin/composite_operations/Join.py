__author__ = 'Michal'

from composite_operations import Selection


class Join:
    def __init__(self, left=False, right=False, condition=None):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__right = right
        self.__left = left
        if condition is not None:
            self.__condition = []
            for cond in condition:
                self.__condition.append(Selection(cond['column1'], cond['condition'], cond['column2']))
        self.__condition = condition
        self.__element = None
        if left and right:
            self.__name = "Full outter join"
        elif left and not right:
            self.__name = "Left outter join"
        elif not left and right:
            self.__name = "Right outter join"
        elif not left and not right:
            self.__name = "Inner join"

    def set(self, ancestor):
        if self.__ancestor_left is None:
            self.__ancestor_left = ancestor
        else:
            self.__ancestor_right = ancestor

    def set_condition(self, condition):
        self.__condition = condition

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
            conditions = []
            for condition in self.__condition:
                c = {}
                c['column1'] = condition.get_left_operand().__str__()
                c['condition'] = condition.get_operator().__str__()
                c['column2'] = condition.get_right_operand().__str__()
                conditions.append(c)
            el.object.values['cond'] = conditions
            self.__element = el
        return self.__element
