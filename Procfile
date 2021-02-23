release: python manage.py makemigrations && python manage.py migrate && python population_script.py
web: gunicorn sleep_surv.wsgi