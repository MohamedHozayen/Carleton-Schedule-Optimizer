web: python manage.py collectstatic --noinput; python gunicorn scheduler.wsgi -b 0.0.0.0:$PORT -w 3
