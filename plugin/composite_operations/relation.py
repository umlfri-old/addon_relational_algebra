from error import CompileError
from sqlparse import tokens as Tokens
import sqlparse
import itertools
from sqlparse import sql as Objects

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
        self.__rows = rows
        self.create_unique()
        return self

    def get_column_index(self, column):
        index = []
        header_name = []
        for i, header in enumerate(self.__header):
            if header.is_equal(column):
                if len(header_name) == 0 and len(index) == 0:
                    index.append(i)
                    header_name.append(header)
                elif isinstance(column.get_real_name(False, False).ttype, type(Tokens.Wildcard)) and column.get_real_name(False, True) == "*":
                    index.append(i)
                    header_name.append(header)
                else:
                    raise ValueError
        if len(index) == 0 and len(header_name) == 0:
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
                raise CompileError("Ambiguously column name detected - '" + column.__str__() + "'", "Projection error")
            except IndexError:
                raise CompileError("'" + column.__str__() + "' not found in table", "Projection error")
            headers = headers + header
            indexes = indexes + index
        for data in self.__rows:
            rows.append([data[i] for i in indexes])
        self.__header = headers
        self.__rows = rows
        return self

    def difference(self, other):
        rows = []
        if self.is_equal_header(other):
            self.split_headers(other)
            for row in self.__rows:
                try:
                    other.getRows().index(row)
                except ValueError:
                    rows.append(row)
            self.__rows = rows
            self.create_unique()
        else:
            raise CompileError("Columns`s names in tables are different", "Difference error")
        return self

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
            self.__rows = rows
            self.create_unique()
        else:
            raise CompileError("Columns`s names in tables are different", "Intersection error")
        return self

    def union(self, other):
        if self.is_equal_header(other):
            self.split_headers(other)
            for row in other.getRows():
                self.__rows.append(row)
            self.create_unique()
        else:
            raise CompileError("Columns`s names in tables are different", "Union error")
        return self

    def create_unique(self):
        self.__rows = [k for k,v in itertools.groupby(sorted(self.__rows))]

    def is_equal_header(self, other):
        header = [o.get_column_name() for o in self.__header]
        other_header = [o.get_column_name() for o in other.getHeader()]
        if header == other_header:
            return True
        return False

    def split_headers(self, other):
        for header in self.__header:
            header.add_table_name(other.get_table_name(header.get_column_name()))

    def difference_headers(self, other):
        headers = []
        for header in self.__header:
            try:
                other.contains_column(header.get_column_name())
            except IndexError:
                if header.get_table_name() is not None or len(header.get_table_name()) != 0:
                    headers.append(sqlparse.parse(header.get_table_name()[0] + "." + header.get_column_name())[0].token_first())
                else:
                    headers.append(sqlparse.parse(header.get_column_name())[0].token_first())
        return headers

    def selection(self, left_operand, operation, right_operand):
        rows = []
        if isinstance(left_operand, Objects.Identifier):
            try:
                index, header = self.get_column_index(left_operand)
            except ValueError:
                raise CompileError("Ambiguously column name detected - '" + left_operand.__str__() + "'", "Projection error")
            except IndexError:
                raise CompileError("'" + left_operand.__str__() + "' not found in table", "Projection error")
            index = index[0]
            left_operand = {"type": "column", "value": index}
        else:
            if left_operand.ttype == Tokens.Literal.Number.Integer:
                left_operand = {"value", int(left_operand.normalized)}
            elif left_operand.ttype == Tokens.Literal.String.Single:
                left_operand = {"value", left_operand.normalized}
            elif left_operand.ttype == Tokens.Literal.Number.Float:
                left_operand = {"value", float(left_operand.normalized)}

        if isinstance(right_operand, Objects.Identifier):
            try:
                index, header = self.get_column_index(right_operand)
            except ValueError:
                raise CompileError("Ambiguously column name detected - '" + right_operand.__str__() + "'", "Projection error")
            except IndexError:
                raise CompileError("'" + right_operand.__str__() + "' not found in table", "Projection error")
            index = index[0]
            right_operand = {"type": "column", "value": index}
        else:
            if right_operand.ttype == Tokens.Literal.Number.Integer:
                right_operand = {"value", int(right_operand.normalized)}
            elif right_operand.ttype == Tokens.Literal.String.Single:
                right_operand = {"value", right_operand.normalized}
            elif right_operand.ttype == Tokens.Literal.Number.Float:
                right_operand = {"value", float(right_operand.normalized)}
        for row in self.__rows:
            if left_operand["type"] == "column":
                left = row[left_operand["value"]]
            else:
                left = left_operand["value"]

    def contains_column(self, column):
        for header in self.__header:
            if header.get_column_name() == column:
                return True
        raise IndexError

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
        if column.get_real_name(False, False).ttype is not None\
                and isinstance(column.get_real_name(False, False).ttype, type(Tokens.Wildcard)) \
                and column.get_real_name(False, True) == "*" \
                and column.get_table_name() in self.__tables_name:
            return True
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



