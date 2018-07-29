web: gunicorn cinemanio.wsgi --log-file -
worker: celery worker --app=cinemanio.celery -l info
beat: celery beat --app=cinemanio.celery -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
