.PHONY: data db export test lint all

data:     ## скачать CSV с Kaggle
	uv run python -m scripts.download

db:       ## пересоздать базу retailrocket и загрузить события
	uv run python -m scripts.build_db

export:   ## выгрузить агрегаты для DataLens в data/datalens/
	uv run python -m scripts.export

test:
	uv run pytest -q

lint:
	uv run ruff check .
	uv run ruff format --check .

all: data db export
