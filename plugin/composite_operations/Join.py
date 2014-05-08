__author__ = 'Michal'

from objects import Condition
import ast
import sqlparse
import copy

class Join:
    def __init__(self, left=False, right=False, condition=None):
        self.__ancestor_left = None
        self.__ancestor_right = None
        self.__right = right
        self.__left = left
        self.__condition = []
        self.__level = 0
        if condition is not None:
            if not isinstance(condition, list):
                condition = ast.literal_eval(condition)
            for c in condition:
                self.__condition.append(Condition(sqlparse.parse(c['column1'])[0].token_first(), c['condition'],
                                                  sqlparse.parse(c['column2'])[0].token_first()))

        self.__element = None
        if left and right:
            self.__name = "Full outter join"
        elif left and not right:
            self.__name = "Left outter join"
        elif not left and right:
            self.__name = "Right outter join"
        elif not left and not right:
            self.__name = "Inner join"
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

    def set_condition(self, condition):
        self.__condition = condition

    def paint(self, interface, diagram, graph, level):
        if self.__element is None:
            connection_left = interface.project.metamodel.connections["Relationship"]
            connection_right = interface.project.metamodel.connections["Relationship"]
            ancestor_element_left, left_position, left_level = self.__ancestor_left.paint(interface, diagram, graph, level)
            ancestor_element_right, right_position, right_level = self.__ancestor_right.paint(interface, diagram, graph, level)
            el = self.create_element(interface, diagram)
            self.__position = len(graph.vs)
            graph.add_vertex(self.__element.object.values['name'])
            graph.add_edge(left_position, self.__position)
            graph.add_edge(right_position, self.__position)
            ancestor_element_left.connect_with(el, connection_left)
            ancestor_element_right.connect_with(el, connection_right)
            level = max(left_level, right_level)
            level += 1
            self.__level = level
            return el, self.__position, self.__level
        else:
            return self.__element, self.__position, self.__level

    def create_element(self, interface, diagram):
        if self.__element is None:
            element = interface.project.metamodel.elements[self.__name]
            el = diagram.create_element(element)
            conditions = []
            if self.__condition is not None:
                for condition in self.__condition:
                    c = {}
                    c['column1'] = condition.get_left_operand().__str__()
                    c['condition'] = condition.get_operator().__str__()
                    c['column2'] = condition.get_right_operand().__str__()
                    conditions.append(c)
                el.object.values['cond'] = conditions
            self.__element = el
        return self.__element

    def execute(self):
        if self.__data is None:
            left_data = self.__ancestor_left.execute()
            right_data = self.__ancestor_right.execute()
            left_data.join(right_data, self.__condition, self.__left, self.__right)
            self.__data = left_data
            return copy.deepcopy(self.__data)
        else:
            return copy.deepcopy(self.__data)