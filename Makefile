.PHONY: check format mypy lint-all

check:
	poetry run ruff check .

format:
	poetry run ruff format .

mypy:
	poetry run mypy --config-file pyproject.toml .

lint-all: check format mypy