install:
	poetry install
run:
	poetry run uvicorn cortex.app:app --reload
test:
	poetry run pytest
lint:
	poetry run ruff check .
format:
	poetry run ruff format .
typecheck:
	poetry run mypy cortex
check: format lint typecheck test
