"""Выгружает агрегаты для DataLens в data/datalens/ — CSV с русскими заголовками."""

from pathlib import Path

import psycopg

from scripts import db
from scripts.queries import run_query

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "datalens"

# имя файла -> (запрос, {колонка запроса: заголовок в CSV})
EXPORTS: dict[str, tuple[str, dict[str, str]]] = {
    "funnel": (
        "10_funnel",
        {
            "step_no": "Номер шага",
            "step": "Шаг",
            "visitors": "Посетители",
            "conv_from_prev": "Конверсия из предыдущего шага",
            "conv_from_start": "Конверсия от первого шага",
        },
    ),
    "funnel_weekly": (
        "11_funnel_weekly",
        {
            "week": "Неделя",
            "visitors": "Смотрели товары",
            "carted": "Положили в корзину",
            "purchased": "Купили",
            "cr_cart": "Конверсия в корзину",
            "cr_purchase": "Конверсия в покупку",
        },
    ),
    "retention": (
        "21_retention",
        {
            "cohort_week": "Когорта",
            "cohort_size": "Размер когорты",
            "week_offset": "Неделя жизни",
            "active": "Активные",
            "retention": "Retention",
        },
    ),
    "buyers": (
        "30_buyers",
        {
            "segment": "Сегмент",
            "visitors": "Посетители",
            "avg_sessions": "Сессий на посетителя",
            "avg_views": "Просмотров на посетителя",
            "median_views_before_purchase": "Медиана просмотров до покупки",
        },
    ),
}


def export_all(conn: psycopg.Connection, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, (query, columns) in EXPORTS.items():
        df = run_query(conn, query).rename(columns=columns)[list(columns.values())]
        path = out_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        paths.append(path)
    return paths


def main() -> None:
    with db.connect("retailrocket") as conn:
        for path in export_all(conn, OUT_DIR):
            print(path.name)


if __name__ == "__main__":
    main()
