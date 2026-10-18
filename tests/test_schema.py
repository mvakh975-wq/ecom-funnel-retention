import psycopg
import pytest

from tests.conftest import query


def test_duplicate_rows_dropped(conn):
    # 18 строк в фикстуре, одна из них — полный дубль
    assert query(conn, "select count(*) from rr.events")[0][0] == 17


def test_category_tree_loaded(conn):
    assert query(conn, "select count(*), count(parent_id) from rr.categories")[0] == (3, 2)


@pytest.mark.parametrize(
    ("event_type", "transaction_id", "error"),
    [
        ("transaction", None, psycopg.errors.CheckViolation),
        ("view", 1, psycopg.errors.CheckViolation),
        ("click", None, psycopg.errors.ForeignKeyViolation),
    ],
)
def test_invalid_events_rejected(conn, event_type, transaction_id, error):
    with pytest.raises(error), conn.transaction():
        conn.execute(
            "insert into rr.events (event_ts, visitor_id, event_type, item_id, transaction_id)"
            " values (now(), 1, %s, 1, %s)",
            (event_type, transaction_id),
        )


def test_database_timezone_is_utc(conn):
    # SQL-файлы должны давать те же недели, если открыть их в psql или DBeaver
    raw = psycopg.connect(dbname="rr_test", host="localhost", user="postgres")
    with raw:
        assert raw.execute("select current_setting('TimeZone')").fetchone()[0] == "UTC"
