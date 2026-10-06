.PHONY: install test lint typecheck check run docker-build

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src/veritrag

check: lint typecheck test

run:
	uvicorn veritrag.api.app:app --reload

docker-build:
	docker build -t veritrag:local .
