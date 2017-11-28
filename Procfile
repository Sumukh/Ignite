web: gunicorn wsgi:app --preload
work: ./manage.py rq worker
schedule: ./manage.py scheduler
