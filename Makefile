up-db:
	docker compose up -d db

down-db:
	docker compose down

migrate:
	python manage.py migrate --settings=menuva.settings

test:
	pytest -v

lint:
	black --check . && flake8

run-local:
	export DJANGO_ENV=local && python manage.py runserver

run-prod:
	export DJANGO_ENV=production && python manage.py runserver 0.0.0.0:8000
