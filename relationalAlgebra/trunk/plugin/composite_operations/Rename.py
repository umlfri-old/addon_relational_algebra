__author__ = 'Michal'

from relation import Relation
from error import CompileError


class Rename:
    def __init__(self, alias, column=None, ancestor=None):
        self.__alias = alias
        self.__ancestor = ancestor
        if column == "":
            self.__column = None
        else:
            self.__column = column
        self.__name = "Rename"
        self.__element = None
        self.__data = None

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
            el.object.values['alias_name'] = self.__alias.__str__()
            if self.__column is not None and self.__column != "":
                el.object.values['attribute_name'] = self.__column.__str__()
            self.__element = el
        return self.__element

    def execute(self):
        if self.__data is None:
            relation = self.__ancestor.execute()
            if self.__column is None:
                relation.setName(self.__alias)
            else:
                try:
                    index = relation.getHeader().index(self.__column)
                except ValueError:
                    raise CompileError("Relation don`t have attribute of name '" + self.__column + "'", "Rename exception")
                relation.getHeader()[index] = self.__alias
            unique_relation = Relation(relation.getHeader(), relation.getName())
            [unique_relation.addRow(list(x)) for x in set(tuple(x) for x in relation)]
            self.__data = unique_relation
            return unique_relation
        else:
            return self.__data

