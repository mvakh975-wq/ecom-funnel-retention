import pandas as pd
import pytest

from scripts.export import EXPORTS, export_all
from scripts.queries import run_query


def test_buyers_vs_non_buyers(conn):
    df = run_query(conn, "30_buyers").set_index("segment")
    assert df.index.tolist() == ["Покупатели", "Не покупали"]
    assert df["visitors"].tolist() == [3, 3]
    assert df["avg_sessions"].tolist() == pytest.approx([4 / 3, 5 / 3], abs=1e-2)
    assert df["avg_views"].tolist() == pytest.approx([5 / 3, 5 / 3], abs=1e-2)
    assert df["median_sessions"].tolist() == [1, 2]
    assert df["median_views"].tolist() == [1, 2]
    # просмотров до первой покупки: V1 — 2, V3 — 0, V5 — 1
    assert df.loc["Покупатели", "median_views_before_purchase"] == 1
    assert pd.isna(df.loc["Не покупали", "median_views_before_purchase"])


def test_export_writes_aggregates_without_ids(conn, tmp_path):
    paths = export_all(conn, tmp_path)
    assert sorted(p.name for p in paths) == sorted(f"{name}.csv" for name in EXPORTS)
    for path in paths:
        df = pd.read_csv(path)
        query, columns = EXPORTS[path.stem]
        assert len(df) > 0
        assert list(df.columns) == list(columns.values())
        # в выгрузку не попадают id посетителей и товаров
        assert not any(col.endswith("_id") for col in columns)
