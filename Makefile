up-db:
	docker compose up -d db

down-db:
	docker compose down

migra:
	python manage.py makemigrations

migrate:
	python manage.py migrate

test:
	pytest -v

lint:
	black --check . && flake8

run:
	export DJANGO_ENV=local && python manage.py runserver

run-prod:
	export DJANGO_ENV=production && python manage.py runserver 0.0.0.0:8000
