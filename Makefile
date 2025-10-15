.PHONY: run, mm, m, s, super

run:
	poetry run python manage.py runserver

mm:
	poetry run python manage.py makemigrations $(app_name)

m:
	poetry run python manage.py migrate

super:
	poetry run python manage.py createsuperuser

s:
	poetry run python manage.py shell_plus --ipython
