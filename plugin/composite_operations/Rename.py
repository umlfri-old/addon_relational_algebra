__author__ = 'Michal'

from relation import Relation
from error import CompileError
import sqlparse

class Rename:
    def __init__(self, alias, column=None, ancestor=None):
        self.__alias = alias
        self.__ancestor = ancestor
        if column == "" or column is None:
            self.__column = None
        else:
            column = sqlparse.parse(column)
            self.__column = column[0].token_first()
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
            relation.rename(self.__column, self.__alias)
            self.__data = relation
        else:
            return self.__data

