# Flask Ignite

Built off of [Flask Foundation](https://jackstouffer.github.io/Flask-Foundation/) and the [bootstrapy project](https://github.com/kirang89/bootstrapy)

Best practices List:
* [Larger Applications With Flask](http://flask.pocoo.org/docs/patterns/packages/).
* [Creating Websites With Flask](http://maximebf.com/blog/2012/10/building-websites-in-python-with-flask/)
* [Getting Bigger With Flask](http://maximebf.com/blog/2012/11/getting-bigger-with-flask/)

## Setup

> make setup

or

```
# Optional: $ virtualenv -p python3 env; source env/bin/activate

pip install -r requirements.txt

```

## Running

```
# Development
./manage.py server

# Production
gunicorn -b 0.0.0.0:5000 wsgi:app
```

## License

This is a commercial product. For library license information see LICENSE.md
