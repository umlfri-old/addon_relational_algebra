from error import CompileError
from sqlparse import tokens as Tokens
import sqlparse
import itertools
from sqlparse import sql as Objects
import datetime
import time
import re
from objects import Condition


class Relation:
    def __init__(self, header=None):
        if header is None:
            self.__header = []
        else:
            self.__header = header
        self.__rows = []
        self.__right_value = {}
        self.__left_value = {}

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

    def addRow(self, row):
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
        columns = []
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

    def get_column_index(self, column, only_column_name=False):
        index = []
        header_name = []
        for i, header in enumerate(self.__header):
            if header.is_equal(column, only_column_name):
                if len(header_name) == 0 and len(index) == 0:
                    index.append(i)
                    header_name.append(header)
                elif isinstance(column.get_real_name(False, False).ttype,
                                type(Tokens.Wildcard)) and column.get_real_name(False, True) == "*":
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
            if isinstance(column.ttype, type(Tokens.Wildcard)) and column.__str__() == "*":
                raise CompileError("Projection does not make any sense here.", "Projection error")
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
        self.__rows = [k for k, v in itertools.groupby(sorted(self.__rows))]

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
                    headers.append(
                        sqlparse.parse(header.get_table_name()[0] + "." + header.get_column_name())[0].token_first())
                else:
                    headers.append(sqlparse.parse(header.get_column_name())[0].token_first())
        return headers

    def process_operand(self, operand):
        op = None
        if isinstance(operand, Objects.Identifier):
            index, header = self.get_column_index(operand)
            index = index[0]
            op = {"type": "column", "value": index}
        else:
            if isinstance(operand, str):
                op = {"type": "string", "value": operand}
            elif operand.ttype == Tokens.Literal.Number.Integer:
                op = {"type": "integer", "value": int(operand.normalized)}
            elif operand.ttype == Tokens.Literal.String.Single:
                operand = operand.normalized
                operand = self.remove_quotes(operand)
                op = {"type": "string", "value": operand.encode("utf-8")}
            elif operand.ttype == Tokens.Literal.Number.Float:
                op = {"type": "float", "value": float(operand.normalized)}
            elif operand.ttype == Tokens.Keyword:
                op = {"type": "keyword", "value": operand.normalized}
            else:
                raise CompileError("Not supported column name", "Selection error")
        return op

    def remove_quotes(self, value):
        if value[0] in '\'' and value[-1] == value[0]:
            operand = value[1:-1]
            return operand
        raise ValueError

    def get_columns_values(self, left_operand, right_operand, operation, row, other_row=None):
        if operation in ("IS", "IS NOT"):
            if right_operand["type"] != "keyword":
                raise CompileError("Excepted NULL keyword with IS or IS NOT comparison", "Selection error")
            else:
                self.__right_value["type"] = "others"
        if other_row is None:
            if left_operand["type"] == "column":
                self.__left_value["type"] = "column"
                left_value = row[left_operand["value"]]
            elif not "value" in self.__left_value:
                self.__left_value["type"] = "others"
                left_value = left_operand["value"]

            if right_operand["type"] == "column":
                self.__right_value["type"] = "column"
                right_value = row[right_operand["value"]]
            elif not "value" in self.__right_value:
                self.__right_value["type"] = "others"
                right_value = right_operand["value"]
        else:
            if left_operand["type"] == "column":
                if left_operand["relation"] == "first":
                    self.__left_value["type"] = "column"
                    left_value = row[left_operand["value"]]
                elif left_operand["relation"] == "second":
                    self.__left_value["type"] = "column"
                    left_value = other_row[left_operand["value"]]
            elif not "value" in self.__left_value:
                self.__left_value["type"] = "others"
                left_value = left_operand["value"]

            if right_operand["type"] == "column":
                if right_operand["relation"] == "first":
                    self.__right_value["type"] = "column"
                    right_value = row[right_operand["value"]]
                elif right_operand["relation"] == "second":
                    self.__right_value["type"] = "column"
                    right_value = other_row[right_operand["value"]]
            elif not "value" in self.__right_value:
                self.__right_value["type"] = "others"
                right_value = right_operand["value"]

        if not "value" in self.__right_value or not "value" in self.__left_value:
            if type(right_value) != type(left_value):
                if isinstance(right_value, datetime.datetime) and not isinstance(left_value, datetime.datetime):
                    left_value = self.parse_date(left_value)
                if isinstance(left_value, datetime.datetime) and not isinstance(right_value, datetime.datetime):
                    right_value = self.parse_date(right_value)

            if operation in ("LIKE", "NOT LIKE"):
                left_value = left_value.__str__()
                right_value = right_value.__str__()
                right_value = right_value.replace(".", "\\.\\")
                right_value = right_value.replace("*", "\\*\\")
                right_value = right_value.replace("_", ".")
                right_value = right_value.replace("%", ".*")

            if operation in ("IN", "NOT IN"):
                if right_value[0] != "(" and right_value[-1] != ")":
                    raise CompileError("Wrong list format in condition. List of values must be in parentheses",
                                       "Selection error")
                right_value = right_value[1:-1]
                right_value = right_value.split(",")
                values = []
                for value in right_value:
                    if isinstance(left_value, str):
                        try:
                            values.append(self.remove_quotes(value))
                        except ValueError:
                            raise CompileError("Wrong string format, must be in quotations ''", "Selection error")
                    elif isinstance(left_value, float):
                        try:
                            values.append(float(value))
                        except ValueError:
                            raise CompileError("Wrong float number", "Selection error")
                    elif isinstance(left_value, int):
                        try:
                            values.append(int(value))
                        except ValueError:
                            raise CompileError("Wrong int number", "Selection error")
                    elif isinstance(left_value, datetime):
                        values.append(self.parse_date(value))
                right_value = values
            self.__right_value["value"] = right_value
            self.__left_value["value"] = left_value
        else:
            if self.__left_value["type"] == "column":
                self.__left_value["value"] = left_value
            if self.__right_value["type"] == "column":
                self.__right_value["value"] = right_value
        return self.__left_value["value"], self.__right_value["value"]

    def parse_date(self, left_value):
        try:
            time_format = "%Y-%m-%d %H:%M:%S"
            value = datetime.datetime.fromtimestamp(time.mktime(time.strptime(left_value, time_format)))
        except ValueError:
            try:
                time_format = "%Y-%m-%d %H:%M:%S"
                left_value = left_value + " 00:00:00"
                value = datetime.datetime.fromtimestamp(time.mktime(time.strptime(left_value, time_format)))
            except ValueError:
                raise CompileError("Value must be in format '%Y-%m-%d %H:%M:%S' or '%Y-%m-%d'", "Selection error")
        return value

    def selection(self, left_operand, operation, right_operand):
        rows = []
        try:
            left_operand = self.process_operand(left_operand)
        except ValueError:
            raise CompileError("Ambiguously column name detected - '" + left_operand.__str__() + "'",
                               "Projection error")
        except IndexError:
            raise CompileError("'" + left_operand.__str__() + "' not found in table", "Projection error")

        try:
            right_operand = self.process_operand(right_operand)
        except ValueError:
            raise CompileError("Ambiguously column name detected - '" + right_operand.__str__() + "'",
                               "Projection error")
        except IndexError:
            raise CompileError("'" + right_operand.__str__() + "' not found in table", "Projection error")

        for row in self.__rows:
            left_value, right_value = self.get_columns_values(left_operand, right_operand, operation, row)
            try:
                if self.compare(left_value, right_value, operation):
                    rows.append(row)
            except ValueError:
                raise CompileError("Types of columns not equal", "Selection error")
        self.__rows = rows
        self.__right_value = {}
        self.__left_value = {}
        return self

    def check_type(self, left, right):
        if left is None and right is not None:
            return False
        if left is not None and right is None:
            return False
        if type(left) != type(right):
            raise ValueError
        return True

    def compare(self, left, right, operation):
        if operation == "=":
            if not self.check_type(left, right):
                return False
            if left == right:
                return True
        elif operation == "<":
            if not self.check_type(left, right):
                return False
            if left < right:
                return True
        elif operation == "<=":
            if not self.check_type(left, right):
                return False
            if left <= right:
                return True
        elif operation == ">":
            if not self.check_type(left, right):
                return False
            if left > right:
                return True
        elif operation == ">=":
            if not self.check_type(left, right):
                return False
            if left >= right:
                return True
        elif operation == "!=":
            if not self.check_type(left, right):
                return False
            if left != right:
                return True
        elif operation == "IS":
            if left is None:
                return True
        elif operation == "IS NOT":
            if left is not None:
                return True
        elif operation == "LIKE":
            a = re.match(right, left.__str__())
            if a is not None:
                return True
        elif operation == "NOT LIKE":
            a = re.match(right, left.__str__())
            if a is None:
                return True
        elif operation == "IN":
            if left in right:
                return True
        elif operation == "NOT IN":
            if left not in right:
                return True
        return False

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

    def join(self, other, conditions, left, right):
        rows = []
        used = []
        if conditions is None or len(conditions) == 0:
            common = False
            for header in self.__header:
                try:
                    index, header_name = other.get_column_index(header.get_column_name(), True)
                    conditions.append(Condition(sqlparse.parse(header.__str__())[0].token_first(),
                                                "=", sqlparse.parse(header_name[0].__str__())[0].token_first()))
                    common = True
                except ValueError:
                    pass
                except IndexError:
                    pass
            if not common:
                raise CompileError("Table don`t have common columns", "Natural join error")
        for condition in conditions:
            try:
                left_operand = self.process_operand(condition.get_left_operand())
                left_operand["relation"] = "first"
            except ValueError:
                raise CompileError(
                    "Ambiguously column name detected - '" + condition.get_left_operand().__str__() + "'",
                    "Projection error")
            except IndexError:
                try:
                    left_operand = other.process_operand(condition.get_left_operand())
                except ValueError:
                    raise CompileError(
                        "Ambiguously column name detected - '" + condition.get_left_operand().__str__() + "'",
                        "Projection error")
                except IndexError:
                    raise CompileError("'" + condition.get_left_operand().__str__() + "' not found in table",
                                       "Projection error")
                left_operand["relation"] = "second"

            try:
                right_operand = self.process_operand(condition.get_right_operand())
                right_operand["relation"] = "first"
            except ValueError:
                raise CompileError(
                    "Ambiguously column name detected - '" + condition.get_right_operand().__str__() + "'",
                    "Projection error")
            except IndexError:
                try:
                    right_operand = other.process_operand(condition.get_right_operand())
                except ValueError:
                    raise CompileError(
                        "Ambiguously column name detected - '" + condition.get_right_operand().__str__() + "'",
                        "Projection error")
                except IndexError:
                    raise CompileError("'" + condition.get_right_operand().__str__() + "' not found in table",
                                       "Projection error")
                right_operand["relation"] = "second"
            for row in self.__rows:
                number = 0
                for r in other.getRows():
                    left_value, right_value = self.get_columns_values(left_operand, right_operand,
                                                                      condition.get_operator(), row, r)
                    try:
                        if self.compare(left_value, right_value, condition.get_operator()):
                            number += 1
                            used.append(r)
                            try:
                                rows.index(row + r)
                            except ValueError:
                                rows.append(row + r)
                        else:
                            try:
                                rows.remove(row + r)
                            except ValueError:
                                pass
                    except ValueError:
                        raise CompileError("Types of columns not equal", "Selection error")
                if number == 0 and left:
                    none = []
                    for i in range(0, len(other.getHeader())):
                        none.append(None)
                    rows.append(row + none)
            if right:
                for r in other.getRows():
                    none = []
                    if r not in used:
                        for i in range(0, len(self.__header)):
                            none.append(None)
                        rows.append(none + r)
        self.__rows = rows
        self.create_unique()
        self.__header = self.__header + other.getHeader()
        for condition in conditions:
            if isinstance(condition.get_left_operand(), Objects.Identifier) \
                    and isinstance(condition.get_right_operand(), Objects.Identifier):
                if condition.get_left_operand().get_real_name(False, True) == condition.get_right_operand().get_real_name(False, True):
                    column = condition.get_left_operand().get_real_name(False, True)
                    indexes = [i for i, x in enumerate(self.__header) if x.get_column_name() == column]
                    self.__header[indexes[0]].add_table_name(self.__header[indexes[1]].get_table_name())
                    del self.__header[indexes[1]]
                    for rows in self.__rows:
                        del rows[indexes[1]]
        return self

    def rename(self, column, alias):
        if column is None:
            for header in self.__header:
                header.rename(alias)
        else:
            try:
                index, header_name = self.get_column_index(column)
            except IndexError:
                raise CompileError("Relation don`t have attribute of name '" + column.__str__() + "'", "Rename exception")
            except ValueError:
                 raise CompileError("Ambiguously column name detected - '" + column.__str__() + "'", "Rename error")
            if len(index) > 1:
                raise CompileError("Ambigously column name detected - '" + column.__str__() + "'", "Rename error")
            self.__header[index[0]].rename_column(alias)
        return self

class Header:
    def __init__(self, column, tables_name):
        self.__column_name = column
        self.__tables_name = tables_name

    def get_column_name(self):
        return self.__column_name

    def rename_table(self, table):
        self.__tables_name = [table]

    def rename_column(self, column):
        self.__column_name = column
    def is_equal(self, column, only_column_name=False):
        if only_column_name:
            if self.__column_name == column:
                return True
        else:
            if column.get_real_name(False, False).ttype is not None \
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

    def __str__(self):
        column = ""
        if self.__tables_name is not None and len(self.__tables_name) != 0:
            column = self.__tables_name[0] + "."
        column = column + self.__column_name
        return column



