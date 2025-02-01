
import pyodbc

# informações de conexão
server = '172.30.4.165,8100'
# database = 'G2_CENSO2023'
database = 'G2_MAN'
username = 'lucas.costa'
password = 'Luc4s301945'


def init_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};SERVER="
        + server
        + ";DATABASE="
        + database
        + ";UID="
        + username
        + ";PWD="
        + password
    )


def run_query(conn, query, *params):
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
