from error import CompileError


class Relation:
    def __init__(self, header=None):
        if header is None:
            self.__header = []
        else:
            self.__header = header
        self.__rows = []

    def __iter__(self):
        for i in self.__rows:
            yield i

    def __getitem__(self, key):
        index = []
        for k in key:
            index.append(self.__header.index(k))
        for r in self.__rows:
            row = []
            for i in index:
                row.append(r[i])
            yield row

    def add_header(self, header):
        self.__header.append(header)

    def addRow(self,row):
        self.__rows.append(row)

    def getHeader(self):
        return self.__header

    def getLen(self):
        return len(self.__rows)

    def getData(self, i=None, y=None):
        if i is None:
            new = []
            for i in self.__rows:
                new.append(i.getData())
            return new
        else:
            return self.__rows[i].getData(y)

    def getColumn(self, i):
        columns=[]
        for row in self.__rows:
            columns.append(row.getData(i))
        return columns

    def product(self, others):
        self.__header = self.__header + others.getHeader()
        rows = []
        for i in self.__rows:
            for y in others.getRows():
                rows.append(i + y)
        self.__rows = set(map(tuple, rows))
        return self.__rows

    def get_column_index(self, column):
        index = None
        header_name = None
        for i, header in enumerate(self.__header):
            if header.is_equal(column):
                if header_name is None and index is None:
                    index = i
                    header_name = header
                else:
                    raise ValueError
        if index is None and header_name is None:
            raise IndexError
        return index, header_name

    def projection(self, columns):
        indexes = []
        headers = []
        rows = []
        for column in columns:
            try:
                index, header = self.get_column_index(column)
            except ValueError:
                raise CompileError("Ambiguously column name detected - '" + column + "'", "Projection error")
            except IndexError:
                raise CompileError("'" + column + "' not found in table", "Projection error")
            headers.append(header)
            indexes.append(index)
        for data in self.__rows:
            rows.append([data[i] for i in indexes])
        self.__header = headers
        self.__rows = rows

    def difference(self, other):
        rows = []
        if self.is_equal_header(other):
            self.split_headers(other)
            for row in self.__rows:
                try:
                    other.getRows().index(row)
                except ValueError:
                    rows.append(row)
            self.__rows = set(map(tuple, rows))
        else:
            raise CompileError("Columns`s names in tables are different", "Difference error")

    def intersection(self, other):
        rows = []
        if self.is_equal_header(other):
            self.split_headers(other)
            for row in self.__rows:
                try:
                    other.getRows().index(row)
                    rows.append(row)
                except ValueError:
                    pass
            self.__rows = set(map(tuple, rows))
        else:
            raise CompileError("Columns`s names in tables are different", "Intersection error")

    def union(self, other):
        if self.is_equal_header(other):
            self.split_headers(other)
            for row in other.getRows():
                self.__rows.append(row)
            self.__rows = set(map(tuple, self.__rows))
        else:
            raise CompileError("Columns`s names in tables are different", "Union error")

    def is_equal_header(self, other):
        header = [o.get_column_name() for o in self.__header]
        other_header = [o.get_column_name() for o in other.getHeader()]
        if header == other_header:
            return True
        return False

    def split_headers(self, other):
        for header in self.__header:
            header.add_table_name(other.get_table_name(header.get_column_name()))

    def get_table_name(self, column):
        for header in self.__header:
            if header.get_column_name() == column:
                return header.get_table_name()

    def setRows(self, rows):
        self.__rows = rows

    def getRows(self):
        return self.__rows


class Header:
    def __init__(self, column, tables_name):
        self.__column_name = column
        self.__tables_name = tables_name

    def get_column_name(self):
        return self.__column_name

    def is_equal(self, column):
        if column.get_real_name(True) == self.__column_name and column.get_table_name() is None:
            return True
        if column.get_table_name() is not None and column.get_table_name() in self.__tables_name \
                and column.get_real_name(True) == self.__column_name:
            return True
        return False

    def add_table_name(self, table_name):
        for table in table_name:
            if table not in self.__tables_name:
                self.__tables_name.append(table)

    def get_table_name(self):
        return self.__tables_name

