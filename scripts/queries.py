"""Выполнение аналитических запросов из папки sql/."""

import pandas as pd
import psycopg

from scripts.db import SQL_DIR

NUMERIC_OID = 1700


def run_query(conn: psycopg.Connection, name: str) -> pd.DataFrame:
    """Выполняет sql/<name>.sql и возвращает результат таблицей.

    Доли и средние в запросах — numeric; в таблице они становятся float.
    """
    with conn.cursor() as cur:
        cur.execute((SQL_DIR / f"{name}.sql").read_text())
        df = pd.DataFrame(cur.fetchall(), columns=[c.name for c in cur.description])
        numeric = [c.name for c in cur.description if c.type_code == NUMERIC_OID]
    return df.astype({col: "float64" for col in numeric})
