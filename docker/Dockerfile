FROM python:3

RUN apk add --update ca-certificates;

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ONBUILD RUN pip install --no-cache-dir -r requirements.txt
ONBUILD COPY . /usr/src/app

CMD gunicorn -w 0.0.0.0:5000 wsgi:app

RUN rm -rf /var/cache/apk/*

EXPOSE 5000
