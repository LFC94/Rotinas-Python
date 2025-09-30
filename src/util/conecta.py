import os
from datetime import datetime

import pyodbc


def init_connection():
    print(f"🔄️ Conectando.... as {datetime.now().strftime('%H%M%S')}")
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        + f"SERVER={os.getenv("SERVER_DB")};"
        + f"DATABASE={os.getenv("DATABASE")};"
        + f"UID={os.getenv("USERNAME_DB")};"
        + f"PWD={os.getenv("PASSWORD_DB")}"
    )


def run_query(conn, query, *params, key=''):
    print(f"🕵️‍♀️ Buscando {key} .... as {datetime.now().strftime('%H%M%S')}")
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results


def run_execute(conn, query, *params):
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor
