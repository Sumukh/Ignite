web: gunicorn -b 0.0.0.0:5000 wsgi:app
work: ./manage.py rq worker
scheduler: ./manage.py rq scheduler
