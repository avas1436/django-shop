.PHONY: up down migrate makemigrations superuser shell logs runserver

up:
	docker compose up -d

build:
	docker compose build

up-build:
	docker compose up --build -d

down:
	docker compose down

migrate:
	docker compose exec backend python manage.py migrate

makemigrations:
	docker compose exec backend python manage.py makemigrations

superuser:
	docker compose exec backend python manage.py createsuperuser

shell:
	docker compose exec backend python manage.py shell

logs:
	docker compose logs -f backend

test:
	docker compose exec backend python manage.py test

runserver:
	uv run --directory core manage.py runserver