__author__ = 'Michal'
import copy

import sqlparse
from composite_operations import *


class Sql_parser:
    def __init__(self):
        pass

    def parse_select(self, object):
        #check if select
        next_index = self.check_select(object)

        #get name of columns
        columns, next_index = self.get_columns(object, next_index)

        #get name of tables
        tables, next_index = self.get_tables(object, next_index)

        #get joins
        joins, next_index = self.get_joins(object, next_index)

        #get condition of select
        conditions, next_index = self.get_condition(object, next_index)
        if len(conditions) != 0 and conditions is not None:
            #group conditions into parenthesis
            conditions = self.group_condition(conditions)

        return Select(columns, tables, joins, conditions)

    def group_condition(self, conditions):
        old_conditions = copy.copy(conditions)
        conditions = []
        if isinstance(old_conditions[0], list):
            group = [self.group_condition(old_conditions[0])]
        else:
            group = [old_conditions[0]]
        for i in range(1, len(old_conditions), 2):
            if old_conditions[i] == "AND":
                group.append(old_conditions[i])
                if isinstance(old_conditions[i + 1], list):
                    group.append(self.group_condition(old_conditions[i + 1]))
                else:
                    group.append(old_conditions[i + 1])
            else:
                conditions.append(group)
                conditions.append(old_conditions[i])
                group = [old_conditions[i+1]]
        conditions.append(group)
        return conditions

    def check_select(self, object):
        actual_object = object.token_first()
        if not isinstance(actual_object.ttype, type(Tokens.DML)):
            raise Exception("not a select statement")
        return object.token_index(actual_object)

    def get_joins(self, object, i):
        conditions = None
        actual_object = object.token_next(i)
        joins = []
        while actual_object is not None and isinstance(actual_object.ttype,type(Tokens.Keyword)) \
                and (actual_object.normalized in("LEFT JOIN", "RIGHT JOIN", "JOIN", "INNER JOIN", "NATURAL JOIN",
                "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "FULL OUTER JOIN")):
            join_type = actual_object.normalized
            i = object.token_index(actual_object)
            table = object.token_next(i)
            #JOIN with SUBSELECT
            if isinstance(table, Objects.Parenthesis):
                i = object.token_index(table)
                table = copy.deepcopy(table)
                table.tokens.pop(0)
                table.tokens.pop(len(table.tokens)-1)
                table_name = self.parse_select(table)
                alias_name = object.token_next(i)
                if len(alias_name.tokens) != 1:
                    alias = alias_name
                    alias_name = alias.token_first()
                    join_condition = alias.token_next(alias.token_index(alias_name))
                    type_join = join_condition.token_first()
                    i = join_condition.token_index(type_join)
                    condition = join_condition.token_next(i)
                else:
                    type_join = object.token_next(object.token_index(alias_name))
                    i = object.token_index(type_join)
                    condition = object.token_next(i)
            elif isinstance(table.token_first(), Objects.Parenthesis):
                table_name = copy.deepcopy(table.token_first())
                table_name.tokens.pop(0)
                table_name.tokens.pop(len(table_name.tokens)-1)
                table_name = self.parse_select(table_name)
                alias_name = table.token_next_by_instance(0, Objects.Identifier)
                join_condition = table.token_next_by_instance(0, Objects.Function)
                if join_condition is not None:
                    type_join = join_condition.token_first()
                    i = join_condition.token_index(type_join)
                    condition = join_condition.token_next(i)
                else:
                    type_join = object.token_next(object.token_index(table))
                    i = object.token_index(type_join)
                    condition = object.token_next(i)
            else:
                if table.token_next_by_instance(0, Objects.Function) is None:
                    i = object.token_index(table)
                    type_join = object.token_next(i)
                    if isinstance(type_join, Objects.Function):
                        actual_object = type_join
                        join_condition = copy.deepcopy(type_join)
                        type_join = join_condition.token_first()
                        condition = join_condition.token_next(join_condition.token_index(type_join))
                    else:
                        if type_join is None and join_type == "NATURAL JOIN":
                           actual_object = table
                        else:
                            i = object.token_index(type_join)
                            condition = object.token_next(i)
                            actual_object = condition
                    subselect = table
                    if isinstance(subselect, Objects.Parenthesis):
                        subselect.tokens.pop(0)
                        subselect.tokens.pop(len(subselect.tokens)-1)
                        table_name = self.parse_select(subselect)
                    else:
                        table_name = table.get_real_name()
                    alias_name = table.get_alias()
                else:
                    actual_object = table
                    table_name = table.token_first().__str__()
                    alias_name = table.token_next_by_instance(0, Objects.Identifier)
                    join_condition = table.token_next_by_instance(0, Objects.Function)
                    type_join = join_condition.token_first()
                    condition = join_condition.token_next(join_condition.token_index(type_join))
            if type_join is not None and type_join.normalized in ("ON", "on"):
                conditions = self.process_condition_join(condition)

            elif type_join is not None and isinstance(type_join.ttype, type(Tokens.Keyword)) and type_join.normalized == "USING":
                raise Exception("using is not supported")

            joins.append(Join_object(table_name, alias_name, join_type, conditions))
            i = object.token_index(actual_object)
            actual_object = object.token_next(i)
        if actual_object is None or isinstance(actual_object.ttype,type(Tokens.Punctuation)):
            return joins, i
        next_object = actual_object.token_next(-1)
        if isinstance(next_object.ttype, type(Tokens.Keyword)) and next_object.normalized == "WHERE":
            return joins, i
        return joins, object.token_index(actual_object)

    def get_condition(self, object, i):
        condition_statement = object.token_next(i)
        if condition_statement is None or isinstance(condition_statement.ttype, type(Tokens.Punctuation)):
            return [], i
        conditions = self.parse_parenthesis(condition_statement)
        return conditions, object.token_index(condition_statement)

    def parse_parenthesis(self, condition_statement):
        conditions = []
        i = 0
        try:
            actual_object = condition_statement.token_next(i)
        except AttributeError:
            raise Exception("error in sql syntax. Excepted WHERE keyword")
        while actual_object is not None:
            if isinstance(actual_object, Objects.Parenthesis):
                conditions.append(self.parse_parenthesis(actual_object))
            elif isinstance(actual_object, Objects.Comparison):
                conditions.append(self.parse_condition(actual_object))
            #NOT IN condition
            elif isinstance(actual_object, Objects.Identifier):
                next = condition_statement.token_next(condition_statement.token_index(actual_object)+1)
                if isinstance(next, Objects.Token) and next.normalized == "BETWEEN":
                    operand = condition_statement.token_next(condition_statement.token_index(next))
                    conditions.append(Condition(actual_object, ">=", operand))
                    operation = condition_statement.token_next(condition_statement.token_index(operand))
                    if operation.normalized != "AND":
                        raise Exception("not supported between operation")
                    else:
                        conditions.append("AND")
                    operand2 = condition_statement.token_next(condition_statement.token_index(operation))
                    conditions.append(Condition(actual_object, "<=", operand2))
                    actual_object = operand2
                else:
                    function = condition_statement.token_next_by_instance(0, (Objects.Function, Objects.Parenthesis))

                    function_statement = copy.deepcopy(function)
                    if isinstance(function_statement, Objects.Parenthesis) and isinstance(function_statement.token_next(0), Objects.IdentifierList):
                        if next is not None and next.normalized == "NOT":
                            conditions.append(Condition(actual_object, "NOT IN", function_statement.normalized))
                        else:
                            conditions.append(Condition(actual_object, "IN", function_statement.normalized))
                    elif isinstance(function_statement, Objects.Parenthesis) and isinstance(function_statement.token_next(0).ttype, type(Tokens.DML)):
                        function_statement.tokens.pop(0)
                        function_statement.tokens.pop(len(function_statement.tokens)-1)
                        if next is not None and next.normalized == "NOT":
                            conditions.append(Condition(actual_object, "NOT IN", self.parse_select(function_statement)))
                        else:
                            conditions.append(Condition(actual_object, "IN", self.parse_select(function_statement)))
                    actual_object = function
            #NOT EXISTS CONDITION
            elif isinstance(actual_object, Objects.Token) and actual_object.normalized == "NOT":
                function = condition_statement.token_next_by_instance(condition_statement.token_index(actual_object), (Objects.Function,Objects.Parenthesis))
                function_statement = copy.deepcopy(function)
                actual_object = function
                function_statement.tokens.pop(0)
                function_statement.tokens.pop(len(function_statement.tokens)-1)
                conditions.append(Condition(self.parse_select(function_statement), "NOT EXISTS", None))
            elif isinstance(actual_object, Objects.Function):
                conditions.append(self.parse_condition(copy.deepcopy(actual_object)))
            elif isinstance(actual_object.ttype,type(Tokens.Punctuation)) and actual_object.normalized == ")":
                break
            elif isinstance(actual_object.ttype,type(Tokens.Token)) and actual_object.normalized == "EXISTS":
                actual_object = condition_statement.token_next_by_instance(condition_statement.token_index(actual_object), Objects.Parenthesis)
                conditions.append(self.parse_condition(copy.deepcopy(actual_object)))
            else:
                raise Exception("not supported join comparison")
            i = condition_statement.token_index(actual_object)
            actual_object = condition_statement.token_next(i)
            if actual_object is None or (isinstance(actual_object.ttype, type(Tokens.Punctuation))
                                         and (actual_object.normalized == ")" or actual_object.normalized == ";")):
                break
            i = condition_statement.token_index(actual_object)
            if isinstance(actual_object.ttype, type(Tokens.Keyword)) and (actual_object.normalized == "AND"
                                                                          or actual_object.normalized == "OR"):
                conditions.append(actual_object.normalized)
                actual_object = condition_statement.token_next(i)
            else:
                raise Exception("missing logical operator AND, OR")
        return conditions

    def process_condition_join(self, condition):
        conditions = []
        i = 0
        actual_object = condition.token_next(i)
        while actual_object is not None:
            if isinstance(actual_object, Objects.Parenthesis):
                conditions.append(self.process_condition_join(actual_object))
            elif isinstance(actual_object, Objects.Comparison):
                conditions.append(self.parse_condition(actual_object))
            elif isinstance(actual_object.ttype,type(Tokens.Punctuation)) and actual_object.normalized == ")":
                break
            else:
                raise Exception("not supported join comparison")
            i = condition.token_index(actual_object)
            actual_object = condition.token_next(i)
            i = condition.token_index(actual_object)
            if isinstance(actual_object.ttype, type(Tokens.Keyword)) and actual_object.normalized == "AND":
                actual_object = condition.token_next(i)
            elif actual_object.normalized == "OR":
                raise Exception("not supported OR in JOIN condition")

        return conditions

    def parse_condition(self,condition):
        if isinstance(condition, Objects.Comparison):
            first_operand = condition.left
            i = condition.token_index(first_operand)
            operator = condition.token_next(i)
            second_operand = condition.right
            return Condition(first_operand, operator, second_operand)
        #condition with EXISTS
        elif isinstance(condition,Objects.Function):
            function_statement = condition.token_next(0)
            function_statement.tokens.pop(0)
            function_statement.tokens.pop(len(function_statement.tokens)-1)
            return Condition(self.parse_select(function_statement), "EXISTS", None)
        elif isinstance(condition,Objects.Parenthesis):
            condition.tokens.pop(0)
            condition.tokens.pop(len(condition.tokens)-1)
            return Condition(self.parse_select(condition), "EXISTS",None)
        else:
            raise Exception("invalid condition syntax")

    def get_tables(self, object, i):
        actual_object = object.token_next(i)
        if isinstance(actual_object.ttype, type(Tokens.Keyword)):
            i = object.token_index(actual_object)
            actual_object = object.token_next(i)
        tables = []
        if isinstance(actual_object, Objects.Identifier):
            tables.append(self.process_table(actual_object, True))
        elif isinstance(actual_object,Objects.IdentifierList):
            for y, identifier in enumerate(actual_object.get_identifiers()):
                if y == 0:
                    tables.append(self.process_table(identifier, True))
                else:
                    tables.append(self.process_table(identifier))
        elif isinstance(actual_object, Objects.Parenthesis):
            table = copy.deepcopy(actual_object)
            table.tokens.pop(0)
            table.tokens.pop(len(table.tokens) - 1)
            i = object.token_index(actual_object)
            actual_object = object.token_next(i)
            if isinstance(actual_object,Objects.Identifier):
                tables.append(Table_object(self.parse_select(table), actual_object.normalized, "FIRST"))
            elif isinstance(actual_object, Objects.IdentifierList):
                for y, identifier in enumerate(actual_object.get_identifiers()):
                    if y == 0:
                        tables.append(Table_object(self.parse_select(table), actual_object.normalized, "FIRST"))
                    else:
                        tables.append(self.process_table(identifier))
            else:
                tables.append(Table_object(self.parse_select(table), None, "FIRST"))
        return tables, object.token_index(actual_object)

    def get_columns(self, object, i):
        actual_object = object.token_next(i)
        columns = []
        if isinstance(actual_object, Objects.Identifier):
            columns.append(self.process_column(actual_object))
        elif isinstance(actual_object, Objects.IdentifierList):
            for identifier in actual_object.get_identifiers():
                columns.append(self.process_column(identifier))
        elif actual_object.ttype in (Tokens.Literal.String.Single, Tokens.Literal.Number.Integer, Tokens.Literal.Number.Float):
            columns.append(Column(None, actual_object.normalized, None))
        return columns, object.token_index(actual_object)


    def process_column(self, column):
        if column.ttype in (Tokens.Literal.String.Single, Tokens.Literal.Number.Integer, Tokens.Literal.Number.Float):
            return Column(None, column.normalized, None, True)
        elif isinstance(column.ttype, type(Tokens.Punctuation)):
            return
        #subselect in select part
        if isinstance(column, Objects.Parenthesis):
            raise Exception("subselect in select part is not supported")
        else:
            return Column(column.get_table_name(), column.get_real_name(), column.get_alias())

    def process_table(self, table, first=False):
        if isinstance(table, Objects.Parenthesis):
            table_name = copy.deepcopy(table)
            table_name.tokens.pop(0)
            table_name.tokens.pop(len(table_name.tokens) - 1)
            if first:
                return Table_object(self.parse_select(table_name), None, "FIRST")
            else:
                return Table_object(self.parse_select(table_name), None, "KART")
        elif isinstance(table.token_first(), Objects.Parenthesis):
            table_name = copy.deepcopy(table.token_first())
            alias = table.token_next_by_instance(0, Objects.Identifier)
            table_name.tokens.pop(0)
            table_name.tokens.pop(len(table_name.tokens) - 1)
            if first:
                return Table_object(self.parse_select(table_name), alias, "FIRST")
            else:
                return Table_object(self.parse_select(table_name), alias, "KART")
        else:
            if first:
                return Table_object(table.get_real_name(), table.get_alias(), "FIRST")
            else:
                return Table_object(table.get_real_name(), table.get_alias(), "KART")

    def process_select(self, select, tables):
        composite = None
        #process table
        if select.get_tables() is not None:
            for table in select.get_tables():
                if not isinstance(table.get_table_name(), Select):
                    if table.get_alias_name() is not None and table.get_alias_name() != "":
                        tables.append(table.get_alias_name().__str__() + ".*")
                    else:
                        tables.append(table.get_table_name().__str__() + ".*")

                if table.get_table_type() == "FIRST":
                    composite = self.process_ancestor(table, tables)
                else:
                    product = Product()
                    product.set(composite)
                    product.set(self.process_ancestor(table, tables))
                    composite = product
        #process joins
        if select.get_joins() is not None:
            for join in select.get_joins():
                if isinstance(join.get_table_name(), Select):
                    tables.append(join.get_alias_name().__str__() + ".*")
                elif join.get_alias_name().__str__() != "" or join.get_alias_name().__str__() is not None:
                    tables.append(join.get_alias_name().__str__() + ".*")
                else:
                    tables.append(join.get_table_name().__str__() + ".*")

                if join.get_join_type() in ("LEFT OUTER JOIN", "LEFT JOIN"):
                    join_com = Join(True)
                elif join.get_join_type() in ("RIGHT OUTER JOIN", "RIGHT JOIN"):
                    join_com = Join(False, True)
                elif join.get_join_type() in ("JOIN", "NATURAL JOIN"):
                    join_com = Join(False, False)
                elif join.get_join_type() in ("FULL OUTER JOIN", "FULL JOIN"):
                    join_com = Join(True, True)

                join_com.set(composite)
                join_com.set(self.process_ancestor(join, tables))
                join_com.set_condition(join.get_conditions())
                composite = join_com

        #process conditions
        composite = self.process_conditions(select.get_conditions(), composite, tables)

        columns = [item for item in select.get_columns() if not item.is_constant()]
        #process columns
        if columns is not None and len(columns) != 0:
            projection = Projection(columns, True)
            projection.set(composite)
            composite = projection

        #process rename
        for column in columns:
            alias = column.get_alias_name()
            if alias is not None and alias != "":
                rename = Rename(alias, column.__str__(), composite)
                composite = rename
        return composite

    def process_conditions(self, conditions, composite, tables):
        left_operand = None
        if conditions is not None and len(conditions) != 0:
            left_operand = self.process_operand(conditions[0], composite, tables)
            for i in range(1, len(conditions), 2):
                #operation
                operation = conditions[i]
                if operation == "AND":
                    #right operand
                    right_operand = self.process_operand(conditions[i+1], left_operand, tables)
                else:
                    right_operand = self.process_operand(conditions[i+1], composite, tables)

                if operation == "AND":
                    #right_operand.set(left_operand)
                    left_operand = right_operand
                elif operation == "OR":
                    union = Union()
                    union.set(left_operand)
                    union.set(right_operand)
                    left_operand = union
        else:
            return composite
        return left_operand

    def process_operand(self, operand, composite, tables):
        if isinstance(operand, list):
            return self.process_conditions(operand, composite, tables)

        if isinstance(operand, Condition) and (operand.get_operator() in ("EXISTS", "NOT EXISTS", "IN", "NOT IN")
                                               and (isinstance(operand.get_right_operand(), Select) or isinstance(operand.get_left_operand(),Select))):
            if operand.get_operator() in ("IN", "NOT IN"):
                condition = operand.get_right_operand().get_conditions()
                if len(operand.get_right_operand().get_columns()) != 1:
                    raise Exception("Error at IN statement")
                if len(condition) == 0:
                    condition.append(Condition(operand.get_right_operand().get_columns()[0], "=", operand.get_left_operand()))
                else:
                    condition.append("AND")
                    condition.append(Condition(operand.get_right_operand().get_columns()[0].__str__(), "=", operand.get_left_operand().__str__()))
                operand.get_right_operand().set_columns(None)
                operand.get_right_operand().set_conditions(None)
                operand.set_left_operand(operand.get_right_operand())
                operand.set_right_operand(condition)
                if operand.get_operator() == "IN":
                    operand.set_operator("EXISTS")
                else:
                    operand.set_operator("NOT EXISTS")

            elif operand.get_operator() in ("EXISTS", "NOT EXISTS"):
                operand.set_right_operand(operand.get_left_operand().get_conditions())
                operand.get_left_operand().set_conditions(None)

            if operand.get_operator() == "EXISTS":
                product = Product()
                product.set(composite)
                product.set(self.process_select(operand.get_left_operand(), []))
                if operand.get_right_operand() is not None or len(operand.get_right_operand()) != 0:
                    selection = self.process_conditions(operand.get_right_operand(), product, tables)
                    exists = selection
                else:
                    exists = product

                if not isinstance(exists, Projection):
                    projection = Projection(tables, True)
                    projection.set(exists)
                    return projection
                else:
                    return exists
            elif operand.get_operator() == "NOT EXISTS":
                product = Product()
                product.set(composite)
                product.set(self.process_select(operand.get_left_operand(), []))

                if operand.get_right_operand() is not None or len(operand.get_right_operand()) != 0:
                    selection = self.process_conditions(operand.get_right_operand(), product, tables)
                    projection = Projection(tables, True)
                    projection.set(selection)
                    difference = Difference()
                    difference.set(composite)
                    difference.set(projection)
                else:
                    difference = Difference()
                    difference.set(composite)
                    difference.set(product)
                return difference
        elif isinstance(operand, Condition):
            selection = Selection(operand.get_left_operand(), operand.get_operator(), operand.get_right_operand())
            selection.set(composite)
            return selection

    def process_ancestor(self, ancestor, tables):
        if isinstance(ancestor, Table_object) or isinstance(ancestor, Join_object):
            if isinstance(ancestor.get_table_name(), Select):
                tab = self.process_select(ancestor.get_table_name(), tables)
            else:
                tab = Table(ancestor.get_table_name())
            if ancestor.get_alias_name() is not None:
                rename = Rename(ancestor.get_alias_name())
                rename.set(tab)
                return rename
            else:
                return tab

    def parse(self, command):
        parsed = sqlparse.parse(sqlparse.format(command, reindent=True, keyword_case="upper"))
        if len(parsed) > 1:
            raise CompileError("You can parse only one SQL query at a time", "Parse error")
        select = self.parse_select(parsed[0])
        tables = []
        return self.process_select(select, tables)
