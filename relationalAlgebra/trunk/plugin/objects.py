__author__ = 'Michal'

from sqlparse import tokens as Tokens
from sqlparse import sql as Objects

class Column:
    def __init__(self,table_name,column_name,alias_name):
        self.__table_name = table_name
        self.__column_name = column_name
        self.__alias_name = alias_name

    def get_table_name(self):
        return self.__table_name

    def get_column_name(self):
        return self.__column_name

    def get_alias_name(self):
        return self.__alias_name


class Table_object:
    def __init__(self, table_name, alias_name, type):
        self.__table_name = table_name
        self.__alias_name = alias_name
        self.__type = type

    def get_table_name(self):
        return self.__table_name

    def get_alias_name(self):
        return self.__alias_name

    def get_table_type(self):
        return self.__type

class Join_object:
    def __init__(self,table_name,alias, join_type, condition):
        self.__table_name = table_name
        self.__alias_name = alias
        self.__join_type = join_type
        self.__conditions = condition

    def get_table_name(self):
        return self.__table_name

    def get_alias_name(self):
        return self.__alias_name

    def get_join_type(self):
        return self.__join_type

    def get_conditions(self):
        return self.__conditions

class Condition:
    def __init__(self,left_operand,operator,right_operand):
        if isinstance(left_operand,Objects.Identifier):
            self.__left_operand = Column(left_operand.get_table_name(),left_operand.get_real_name(),None)
        else:
            self.__left_operand = left_operand

        self.__operator = operator
        if isinstance(right_operand,Objects.Identifier):
            self.__right_operand = Column(right_operand.get_table_name(),right_operand.get_real_name(),None)
        else:
            self.__right_operand = right_operand
#
    def get_left_operand(self):
        return self.__left_operand

    def get_right_operand(self):
        return self.__right_operand

    def get_operator(self):
        return self.__operator


class Select:
    def __init__(self, columns, tables, joins, conditions):
        self.__columns = columns
        self.__tables = tables
        self.__joins = joins
        self.__conditions = conditions

    def get_conditions(self):
        return self.__conditions

    def get_tables(self):
        return self.__tables

    def get_joins(self):
        return self.__joins