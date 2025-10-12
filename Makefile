.PHONY: run, mm, m

run:
	poetry run python manage.py runserver

mm:
	poetry run python manage.py makemigrations $(app_name)

m:
	poetry run python manage.py migrate
