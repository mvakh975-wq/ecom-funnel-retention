from datetime import date

import pytest

from scripts.queries import run_query


def test_funnel_is_ordered_per_visitor(conn):
    df = run_query(conn, "10_funnel")
    # 6 посетителей смотрели товары; корзина после просмотра — у 3;
    # покупка после корзины — только у 1 (V3 купил без просмотра, V5 купил раньше корзины)
    assert df["step"].tolist() == ["Просмотр", "Корзина", "Покупка"]
    assert df["visitors"].tolist() == [6, 3, 1]
    assert df["conv_from_prev"].tolist()[1:] == pytest.approx([0.5, 1 / 3], abs=1e-4)
    assert df["conv_from_start"].tolist() == pytest.approx([1.0, 0.5, 1 / 6], abs=1e-4)


def test_weekly_funnel_only_full_weeks(conn):
    df = run_query(conn, "11_funnel_weekly")
    assert df["week"].tolist() == [date(2015, 6, 1), date(2015, 6, 8)]
    assert df["visitors"].tolist() == [3, 3]
    assert df["carted"].tolist() == [2, 1]
    assert df["purchased"].tolist() == [1, 0]
    assert df["cr_purchase"].tolist() == pytest.approx([1 / 3, 0.0], abs=1e-4)


def test_buyers_outside_ordered_funnel(conn):
    df = run_query(conn, "12_funnel_gaps")
    row = df.iloc[0]
    # покупали V1, V3, V5; в упорядоченную воронку попал только V1;
    # V3 ни разу не клал товар в корзину, у V5 корзина после покупки
    assert (row["buyers"], row["in_ordered_funnel"], row["never_carted"]) == (3, 1, 1)
    assert row["share_outside_funnel"] == pytest.approx(2 / 3, abs=1e-4)
