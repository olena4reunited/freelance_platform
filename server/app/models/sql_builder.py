from typing import Callable
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
        self.params = tuple()

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
        self.params += tuple(params.values())
        
        return self
    
    def _process_conditions(self, conditions, operator):
        grouped_parts = []
        
        for condition in conditions:
            if callable(condition):
                temp = SQLBuilder()
                condition(temp)

                if temp.where_columns:
                    grouped_parts.extend(
                        sql.SQL("{} {} {}").format(
                            sql.Identifier(temp.where_columns[i]),
                            sql.SQL(temp.where_operators[i]),
                            sql.Placeholder()
                        )
                        for i in range(len(temp.where_columns))
                    )
                    self.params += tuple(temp.params.values())
            else:
                grouped_parts.append(condition)

        if grouped_parts:
            return sql.SQL("(") + sql.SQL(f" {operator} ").join(grouped_parts) + sql.SQL(")")
        return None
    
    def and_(self, *conditions):
        if not conditions:
            return self

        grouped_parts = self._process_conditions(*conditions, "AND")
        if grouped_parts:
            self.grouped_parts.append(grouped_parts)

        return self

    def or_(self, *conditions):
        if not conditions:
            return self

        grouped_parts = self._process_conditions(*conditions, "OR")
        if grouped_parts:
            self.grouped_parts.append(grouped_parts)

        return self


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
                query += sql.SQL(" AND ").join(self.grouped_parts)

        return query, self.params
   

try:
    with PostgresDatabase() as db:
        with db.connection.cursor() as cursor:        
            query, params = (
                SQLBuilder("users") \
                .select("username") \
                .and_(
                    lambda q: q.where("is_blocked", is_blocked=None),
                    lambda q: q.or_(
                        lambda q: q.where("id", id=20),
                        lambda q: q.where("id", id=2)
                    )
                ) \
                .get()
            )
            query, params = (
                SQLBuilder("users") \
                .select("username") \
                .or_(
                    lambda q: q.where("id", id=20),
                    lambda q: q.where("id", id=2)
                ) \
                .get()
            )
            # query, params = SQLBuilder("users").select().where("username", "=", username='reptilia"; DROP TABLE users;').get()
            # query, params = SQLBuilder("users").select().where("username", "=", username="' OR 1=1 --").get()

            cursor.execute(query, params)

            logger.info("\x1b[1m%s\x1b[0m", query.as_string(cursor))
            logger.info("\x1b[1m%s\x1b[0m", params)
            logger.info("\x1b[1;32m%s\x1b[0m", cursor.fetchall())
except Exception as e:
    traceback.format_exception(e)
    logger.error(
        "Error was occured:\n%s\x1b[31m%s\x1b[0m",
        " "*10,
        repr(e)
    )
