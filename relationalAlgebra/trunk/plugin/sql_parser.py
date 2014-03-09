__author__ = 'Michal'
import sqlparse
from objects import *
from composite_operations import *
import copy


class Sql_parser:
    def __init__(self):
        pass
    def parse_select(self,object):
        #check if select
        next_index = self.check_select(object)

        #get name of columns
        columns, next_index = self.get_columns(object, next_index)

        #get name of tables
        tables, next_index = self.get_tables(object,next_index)

        #get joins
        joins, next_index = self.get_joins(object,next_index)

        #get condition of select
        condition, next_index = self.get_condition(object,next_index)

        return Select(columns,tables,joins,condition)


    def check_select(self,object):
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
            if isinstance(table,Objects.Parenthesis):
                i = object.token_index(table)
                table = copy.deepcopy(table)
                table.tokens.pop(0)
                table.tokens.pop(len(table.tokens)-1)
                table_name = self.parse_select(table)
                alias_name = object.token_next(i)
                type_join = object.token_next(object.token_index(alias_name))
                i = object.token_index(type_join)
                condition = object.token_next(i)
            elif isinstance(table.token_first(), Objects.Parenthesis):
                table_name = copy.deepcopy(table.token_first())
                table_name.tokens.pop(0)
                table_name.tokens.pop(len(table_name.tokens)-1)
                table_name =  self.parse_select(table_name)
                alias_name = table.token_next_by_instance(0,Objects.Identifier)
                type_join = object.token_next(object.token_index(table))
                i = object.token_index(type_join)
                condition = object.token_next(i)


            else:
                i = object.token_index(table)
                type_join = object.token_next(i)
                i = object.token_index(type_join)
                condition = object.token_next(i)
                subselect = table.token_first()
                if isinstance(subselect,Objects.Parenthesis):
                    subselect.tokens.pop(0)
                    subselect.tokens.pop(len(subselect.tokens)-1)
                    table_name =  self.parse_select(subselect)
                else:
                    table_name = table.get_real_name()
                alias_name = table.get_alias()

            if isinstance(type_join.ttype, type(Tokens.Keyword)) and type_join.normalized == "ON":
                conditions =  self.process_condition_join(condition)
            elif isinstance(type_join.ttype, type(Tokens.Keyword)) and type_join.normalized == "USING":
                raise Exception("using is not supported")

            joins.append(Join_object(table_name,alias_name , join_type, conditions))
            i = object.token_index(condition)
            actual_object = object.token_next(i)
        if actual_object is None or isinstance(actual_object.ttype,type(Tokens.Punctuation)):
            return joins, i
        next_object = actual_object.token_next(-1)
        if isinstance(next_object.ttype, type(Tokens.Keyword)) and next_object.normalized == "WHERE":
            return joins, i
        return joins, object.token_index(actual_object)


    def get_condition(self,object, i):
        condition_statement = object.token_next(i)
        if condition_statement is None or isinstance(condition_statement.ttype,type(Tokens.Punctuation)):
            return None, i
        conditions = self.parse_parenthesis(condition_statement)
        return conditions,object.token_index(condition_statement)


    def parse_parenthesis(self,condition_statement):
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
                if next is not None and next.normalized == "NOT":
                    function = condition_statement.token_next_by_instance(0, Objects.Function)
                    function_statement = copy.deepcopy(function.token_next(0))
                    if isinstance(function_statement, Objects.Parenthesis) and isinstance(function_statement.token_next(0), Objects.IdentifierList):
                        conditions.append(Condition(actual_object, "NOT IN", function_statement.normalized))
                    elif isinstance(function_statement, Objects.Parenthesis) and isinstance(function_statement.token_next(0).ttype, type(Tokens.DML)):
                        function_statement.tokens.pop(0)
                        function_statement.tokens.pop(len(function_statement.tokens)-1)
                        conditions.append(Condition(actual_object, "NOT IN", self.parse_select(function_statement)))
                else:
                    conditions.append(self.parse_condition(actual_object))
            #NOT EXISTS CONDITION
            elif isinstance(actual_object, Objects.Token) and actual_object.normalized == "NOT":
                function = condition_statement.token_next_by_instance(condition_statement.token_index(actual_object), (Objects.Function, Objects.Parenthesis))
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
                actual_object = condition_statement.token_next_by_instance(condition_statement.token_index(actual_object),Objects.Parenthesis)
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

        return conditions


    def process_condition_join(self,condition):
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
        #condition with IN
        elif isinstance(condition, Objects.Identifier):
            first_operand = condition.token_first()
            operator = condition.token_next(condition.token_index(first_operand))
            second_operand = operator.token_next(0)
            if isinstance(second_operand, Objects.Parenthesis) and isinstance(second_operand.token_next(0), Objects.IdentifierList):
                return Condition(first_operand, "IN", second_operand.normalized)
            elif isinstance(second_operand, Objects.Parenthesis) and isinstance(second_operand.token_next(0).ttype, type(Tokens.DML)):
                second_operand.tokens.pop(0)
                second_operand.tokens.pop(len(second_operand.tokens) - 1)
                return Condition(first_operand, "IN", self.parse_select(second_operand))
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
            print "tu som "
            for y, identifier in enumerate(actual_object.get_identifiers()):
                if y == 0:
                    tables.append(self.process_table(identifier, True))
                else:
                    if isinstance(identifier, Objects.Parenthesis):
                        table = copy.deepcopy(identifier)
                        table.tokens.pop(0)
                        table.tokens.pop(len(table.tokens) - 1)
                        i = object.token_index(actual_object)
                        actual_object = object.token_next(i)
                        if isinstance(actual_object,Objects.Identifier):
                            tables.append(Table_object(self.parse_select(table), actual_object.normalized, "KART"))
                        elif isinstance(actual_object, Objects.IdentifierList):
                            for y, identifier in enumerate(actual_object.get_identifiers()):
                                if y == 0:
                                    tables.append(Table_object(self.parse_select(table), actual_object.normalized, "KART"))
                                else:
                                    tables.append(self.process_table(identifier))
                        else:
                            tables.append(Table_object(self.parse_select(table), None, "KART"))
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


    def process_column(self,column):
        #subselect in select part
        if isinstance(column.token_first(), Objects.Parenthesis):
            raise Exception("subselect in select part is not supported")
        else:
            return Column(column.get_table_name(), column.get_real_name(), column.get_alias())


    def process_table(self,table,first=False):
        if isinstance(table.token_first(), Objects.Parenthesis):
            raise Exception("subselect in table part is not supported")
        else:
            if first:
                return Table_object(table.get_real_name(), table.get_alias(), "FIRST")
            else:
                return Table_object(table.get_real_name(), table.get_alias(), "KART")


    def process_select(self,select):
        composite = None
        #process table
        if select.get_tables() is not None:
            for table in select.get_tables():
                if table.get_table_type() == "FIRST":
                    composite = self.process_ancestor(table)
                else:
                    product = Product()
                    product.set(composite)
                    product.set(self.process_ancestor(table))
                    composite = product
        #process joins
        if select.get_joins() is not None:
            for join in select.get_joins():
                if join.get_join_type() in ("LEFT OUTER JOIN", "LEFT JOIN"):
                    join_com = Join(True)
                elif join.get_join_type() in ("RIGHT OUTER JOIN", "RIGHT JOIN"):
                    join_com = Join(False, True)
                elif join.get_join_type() in ("JOIN", "NATURAL JOIN"):
                    join_com = Join(False, False)
                elif join.get_join_type() in ("FULL OUTER JOIN", "FULL JOIN"):
                    join_com = Join(True, True)

                join_com.set(composite)
                join_com.set(self.process_ancestor(join))
                join_com.set_condition(join.get_conditions())
                composite = join_com
        #process conditions
        composite =  self.process_conditions(select.get_conditions(), composite)

        #process columns
        if select.get_columns() is not None and len(select.get_columns()) != 0:
            projection = Projection(select.get_columns())
            projection.set(composite)
            composite = projection

        return composite


    def process_conditions(self,conditions, composite):
        left_operand = None
        if conditions is not None:
            left_operand = self.process_operand(conditions[0], composite)
            for i in range(1,len(conditions), 2):
                #operation
                operation = conditions[i]
                #right operand
                right_operand = self.process_operand(conditions[i+1], composite)

                if operation == "AND":
                    right_operand.set(left_operand)
                    left_operand = right_operand
                elif operation == "OR":
                    union = Union()
                    union.set(left_operand)
                    union.set(right_operand)
                    left_operand = union
        else:
            return composite
        return left_operand


    def process_operand(self, operand, composite):
        if isinstance(operand, list):
            return self.process_conditions(operand, composite)
        if isinstance(operand,Condition) and (operand.get_operator() in ("EXISTS","NOT EXISTS")):
            selection = self.process_select(operand.get_left_operand())
            if operand.get_operator() == "EXISTS":
                operation = Intersection()
            else:
                operation = Difference()
            operation.set(composite)
            operation.set(selection)
            return operation
        if isinstance(operand, Condition):
            selection = Selection(operand.get_left_operand(), operand.get_operator(), operand.get_right_operand())
            selection.set(composite)
            return selection


    def process_ancestor(self,ancestor):
        if isinstance(ancestor, Table_object) or isinstance(ancestor, Join_object):
            if isinstance(ancestor.get_table_name(),Select):
                tab = self.process_select(ancestor.get_table_name())
            else:
                tab = Table(ancestor.get_table_name())
            if ancestor.get_alias_name() is not None:
                rename = Rename(ancestor.get_alias_name())
                rename.set(tab)
                return rename
            else:
                return tab


    def parse(self,command):
        parsed = sqlparse.parse(sqlparse.format(command, reindent=True,keyword_case="upper"))
        select = self.parse_select(parsed[0])
        return self.process_select(select)
