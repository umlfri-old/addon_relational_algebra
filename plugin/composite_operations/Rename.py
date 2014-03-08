__author__ = 'Michal'


class Rename:
    def __init__(self, alias,ancestor=None):
        self.__alias = alias
        self.__ancestor = ancestor
        self.__name = "Rename"
        self.__element = None

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
            el.object.values['name'] = self.__alias.__str__()
            self.__element = el
        return self.__element
