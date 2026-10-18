from datetime import date

import pytest

from scripts.queries import run_query
from tests.conftest import query


@pytest.mark.parametrize(("visitor_id", "sessions"), [(1, 2), (2, 2), (3, 1)])
def test_session_breaks_after_30_minutes(conn, visitor_id, sessions):
    # V2: пауза 31 минута — новая сессия; V3: пауза 29 минут — та же сессия
    sql = "select count(*) from rr.sessions where visitor_id = %s"
    assert query(conn, sql, (visitor_id,))[0][0] == sessions


def test_session_flags(conn):
    rows = query(
        conn,
        "select visitor_id, session_no, n_events, has_cart, has_purchase from rr.sessions"
        " where visitor_id in (1, 3) order by visitor_id, session_no",
    )
    assert rows == [(1, 1, 5, True, True), (1, 2, 1, False, False), (3, 1, 2, False, True)]


def test_retention_by_weekly_cohorts(conn):
    df = run_query(conn, "21_retention")
    rows = list(df[["cohort_week", "cohort_size", "week_offset", "active"]].itertuples(False))
    # Когорта 1 июня: V1, V2, V3; на следующей неделе вернулся только V1.
    # Когорта 8 июня: V4, V5; неделя 15 июня неполная — строки для неё нет.
    assert [tuple(r) for r in rows] == [
        (date(2015, 6, 1), 3, 0, 3),
        (date(2015, 6, 1), 3, 1, 1),
        (date(2015, 6, 8), 2, 0, 2),
    ]
    assert df["retention"].tolist() == pytest.approx([1.0, 1 / 3, 1.0], abs=1e-4)


def test_retention_summary_pools_cohorts(conn):
    df = run_query(conn, "22_retention_summary")
    # неделя 1 есть только у когорты 1 июня: 1 из 3 вернулся
    assert df["week_offset"].tolist() == [0, 1]
    assert df["cohorts"].tolist() == [2, 1]
    assert df["retention"].tolist() == pytest.approx([1.0, 1 / 3], abs=1e-4)
