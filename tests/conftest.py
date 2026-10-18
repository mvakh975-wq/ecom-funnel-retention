from pathlib import Path

import pytest

from scripts import db

FIXTURES = Path(__file__).parent / "fixtures"
TEST_DB = "rr_test"


@pytest.fixture(scope="session")
def conn():
    """Свежая тестовая база с загруженными фикстурами."""
    db.recreate_database(TEST_DB)
    with db.connect(TEST_DB) as conn:
        db.build(conn, FIXTURES / "events.csv", FIXTURES / "category_tree.csv")
        yield conn


def query(conn, sql: str, params=None) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()
