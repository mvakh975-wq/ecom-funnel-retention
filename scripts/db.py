"""Подключение к PostgreSQL и сборка базы из CSV.

Параметры подключения берутся из стандартных переменных libpq (PGHOST, PGPORT, PGUSER,
PGPASSWORD или ~/.pgpass); по умолчанию — localhost и пользователь postgres.
"""

import os
from pathlib import Path

import psycopg
from psycopg import sql

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"

RAW_TABLES = {
    "raw_events": (
        "timestamp bigint, visitorid bigint, event text, itemid bigint, transactionid bigint"
    ),
    "raw_category_tree": "categoryid bigint, parentid bigint",
}


def connect(dbname: str) -> psycopg.Connection:
    return psycopg.connect(
        dbname=dbname,
        host=os.environ.get("PGHOST", "localhost"),
        user=os.environ.get("PGUSER", "postgres"),
        options="-c TimeZone=UTC",  # недели и даты считаются в UTC
        autocommit=True,
    )


def recreate_database(dbname: str) -> None:
    with connect("postgres") as conn:
        name = sql.Identifier(dbname)
        conn.execute(sql.SQL("drop database if exists {} with (force)").format(name))
        conn.execute(sql.SQL("create database {}").format(name))
        # недели и даты в SQL считаются в UTC при любом клиенте (psql, DBeaver)
        conn.execute(sql.SQL("alter database {} set timezone to 'UTC'").format(name))


def run_sql_file(conn: psycopg.Connection, path: Path) -> None:
    conn.execute(path.read_text())


def copy_csv(conn: psycopg.Connection, table: str, csv_path: Path) -> None:
    query = sql.SQL("copy {} from stdin with (format csv, header true)").format(
        sql.Identifier(table)
    )
    with conn.cursor() as cur, cur.copy(query) as copy, csv_path.open("rb") as f:
        while chunk := f.read(1 << 20):
            copy.write(chunk)


def build(conn: psycopg.Connection, events_csv: Path, categories_csv: Path) -> int:
    """Создаёт схему rr, загружает CSV и возвращает число строк в rr.events."""
    run_sql_file(conn, SQL_DIR / "01_schema.sql")
    with conn.transaction():
        for table, columns in RAW_TABLES.items():
            conn.execute(
                sql.SQL("create temp table {} ({}) on commit drop").format(
                    sql.Identifier(table), sql.SQL(columns)
                )
            )
        copy_csv(conn, "raw_events", events_csv)
        copy_csv(conn, "raw_category_tree", categories_csv)
        run_sql_file(conn, SQL_DIR / "02_load.sql")
    run_sql_file(conn, SQL_DIR / "03_views.sql")
    return conn.execute("select count(*) from rr.events").fetchone()[0]
