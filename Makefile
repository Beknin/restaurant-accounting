.PHONY: install test test-unit run docker-up docker-down docker-build

install:
	poetry install

test:
	poetry run pytest tests/

test-unit:
	poetry run pytest tests/unit/

run:
	poetry run python app/ui/main.py

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-build:
	docker build -t restaurant-accounting .