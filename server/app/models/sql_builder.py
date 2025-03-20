import traceback

from psycopg2 import sql

from server.app.database.database import PostgresDatabase
from server.app.utils.logger import logger


ALLOWED_OPERATORS = {
    "<", ">", "=", "<=", ">=", "<>", "IS", "IS NOT", "IN", "NOT IN", "LIKE", "ILIKE"
}


class SQLBuilder:
    def __init__(self, table_name: str | None = None):
        self.table_name = table_name
        self.select_columns = []
        self.where_columns = []
        self.grouped_parts = []
        self.where_operators = []
        self.join_clauses = []
        self.group_by_columns = []
        self.having_colnditions = []
        self.limit = None
        self.offset = None
        self.params = []

    class Group:
        def __init__(self, parent, operator, column: str, param: str, query_operator: str = None):
            self.parent = parent
            self.operator = f" {operator} "
            self.conditions = []
            self.params = []

            self._add(column=column, param=param, operator=query_operator)


        def _add(self, column: str, param: str, operator: str = None):
            if not operator:
                if param is None:
                    operator = "IS"
                else:
                    operator = "="

            if operator.upper() not in ALLOWED_OPERATORS:
                raise ValueError("Unsupported operator. Could not excute the query")

            self.conditions.append(
                sql.SQL("{} {} {}").format(
                    sql.Identifier(column),
                    sql.SQL(operator),
                    sql.Placeholder()
                )
            )
            self.params.append(param)

            return self

        def AND(self, column: str, param: str, operator: str = None):
            if self.operator != " AND ":
                raise ValueError("You are not allowed to use this operator")

            return self._add(column=column, param=param, operator=operator)

        def OR(self, column: str, param: str, operator: str = None):
            if self.operator != " OR ":
                raise ValueError("You are not allowed to use this operator")

            return self._add(column=column, param=param, operator=operator)

        def add_group(self, group):
            self.conditions.append(sql.SQL("({})").format(group.comb()[0]))
            self.params.extend(group.params)

            return self

        def comb(self):
            return sql.SQL(self.operator).join(
                condition
                for condition in self.conditions
            ), self.params
        
        def end(self):
            return self.parent

    def select(self, *columns):
        if columns:
            self.select_columns.extend(columns)
        if not columns:
            self.select_columns.append("*")     
        return self

    def where(self, where_column: str, operator: str = None, **params):
        if not operator:
            if None in params.values():
                operator = "IS"
            else:
                operator = "="

        if operator.upper() not in ALLOWED_OPERATORS:
            raise ValueError("Unsupported operator. Could not excute the query")

        self.where_columns.append(where_column)
        self.where_operators.append(operator)
        self.params.extend(params.values())

        return self

    def AND(self, column, param, operator = None):
        group = self.Group(
            parent=self,
            operator="AND",
            column=column,
            param=param,
            query_operator=operator
        )
        self.grouped_parts.append(group)
        return group

    def OR(self, column, param, operator = None):
        group = self.Group(
            parent=self,
            operator="OR",
            column=column,
            param=param,
            query_operator=operator
        )
        self.grouped_parts.append(group)
        return group

    def get(self):
        if self.select_columns:
            query = sql.SQL("SELECT {} FROM {}").format(
                sql.SQL(", ").join(
                    sql.Identifier(column) if column != "*" else sql.SQL("*")
                    for column in self.select_columns
                ),
                sql.Identifier(self.table_name)
            )
            
        if self.where_columns or self.grouped_parts:
            query += sql.SQL(" WHERE ")

            if self.where_columns:    
                query += sql.SQL(" AND ").join(
                    sql.SQL("{} {} {}").format(
                        sql.Identifier(self.where_columns[i]),
                        sql.SQL(self.where_operators[i]),
                        sql.Placeholder()
                    )
                    for i in range(len(self.where_columns))
                )

            if self.grouped_parts:
                group_queries = []
                group_params = []

                for group in self.grouped_parts:
                    query_part, params = group.comb()
                    group_queries.append(query_part)
                    group_params.extend(params)

                query += sql.SQL(" AND ").join(group_queries)
                self.params.extend(group_params)

        return query, self.params


# try:
#     with PostgresDatabase() as db:
#         with db.connection.cursor() as cursor:
#             # sql_builder = SQLBuilder("users").select("username").AND(column="is_blocked", param=None).add_group(SQLBuilder().OR(column="id", param="2").OR(column="id", param="20")).end()
#             # print(sql_builder) 

#             query, params = SQLBuilder("payments").select("id", "payment").where("user_id", params=4).get()


#             logger.info("\x1b[1m%s\x1b[0m", query.as_string(cursor))

#             cursor.execute(query, params)

#             logger.info("\x1b[1m%s\x1b[0m", params)
#             logger.info("\x1b[1;32m%s\x1b[0m", cursor.fetchall())
# except Exception as e:
#     traceback.print_exc()
#     logger.error(
#         "Error was occured:\n%s\x1b[31m%s\x1b[0m",
#         " "*10,
#         repr(e)
#     )
