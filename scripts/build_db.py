"""Пересоздаёт базу retailrocket и загружает в неё данные из data/raw/."""

from pathlib import Path

from scripts import db

DB_NAME = "retailrocket"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def main() -> None:
    db.recreate_database(DB_NAME)
    with db.connect(DB_NAME) as conn:
        n = db.build(conn, RAW_DIR / "events.csv", RAW_DIR / "category_tree.csv")
    print(f"rr.events: {n:,} строк".replace(",", " "))


if __name__ == "__main__":
    main()
