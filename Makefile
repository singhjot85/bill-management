.PHONY: run, mm, m, s

run:
	poetry run python manage.py runserver

mm:
	poetry run python manage.py makemigrations $(app_name)

m:
	poetry run python manage.py migrate

s:
	poetry run python manage.py shell_plus --ipython
