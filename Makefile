.PHONY: install test test-unit run

install:
	poetry install

test:
	poetry run pytest tests/

test-unit:
	poetry run pytest tests/unit/

run:
	poetry run python app/ui/main.py