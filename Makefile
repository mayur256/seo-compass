.PHONY: build up down migrate test lint format

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

migrate:
	docker-compose exec web alembic upgrade head

test:
	pytest

lint:
	ruff check .
	mypy .

format:
	black .
	ruff --fix .