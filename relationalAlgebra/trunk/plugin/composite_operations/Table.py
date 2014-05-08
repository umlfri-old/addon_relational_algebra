__author__ = 'Michal'


from relation import *
import copy


class Table:
    def __init__(self, table, connection=None):
        self.__table = table
        if table == "":
            raise CompileError("Table error. You must type name of table", "Compile error")
        self.__name = "Table"
        self.__element = None
        self.__connection = connection
        self.__data = None
        self.__position = None

    def get_position(self):
        return self.__position

    def paint(self, interface, diagram, graph, level):
        self.create_element(interface, diagram)
        self.__position = len(graph.vs)
        graph.add_vertex(self.__element.object.values['name'])
        level += 1
        return self.__element, self.__position, level

    def move(self, cords):
        self.__element.move(cords[self.__position])

    def create_element(self, interface, diagram):
        if self.__element is None:
            element = interface.project.metamodel.elements[self.__name]
            el = diagram.create_element(element)
            el.object.values['table_name'] = self.__table
            self.__element = el
        return self.__element

    def execute(self):
        if self.__data is None:
            try:
                header = self.__connection.getColumns(self.__table)
                table_header = []
                for h in header:
                    table_header.append(Header(h, [self.__table]))
                relation = Relation(table_header)
            except CompileError as e:
                raise CompileError(e.getValue(), e.getName())
            try:
                data = self.__connection.getData(self.__table)
            except CompileError as e:
                raise CompileError(e.getValue(), e.getName())

            for i in range(0, len(data)):
                new = []
                for y in range(0, len(data[i])):
                    new.append(data[i][y])
                relation.addRow(new)
            relation.create_unique()
            self.__data = relation
            return copy.copy(self.__data)
        else:
            return copy.copy(self.__data)

