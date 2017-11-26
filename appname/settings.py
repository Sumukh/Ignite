import os
import tempfile

class Config(object):
    SECRET_KEY = 'REPLACE MEasdaappnamesdas#!3de*o0alas'  # run flask generate_secret_key
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TWITTER_CONSUMER_KEY = 'xBeXxg9lyElUgwZT6AZ0A'
    TWITTER_CONSUMER_SECRET = 'aawnSpNTOVuDCjx7HMh6uSXetjNN8zWLpZwCEU4LBrk'

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.mailgun.org')
    MAIL_PORT = os.getenv('MAIL_SERVER_PORT', 2525)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'postmaster@email.sumukh.me')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'appname <admin@appname.com>'

    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

class ProdConfig(Config):
    ENV = 'prod'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        'sqlite:///../database.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    # Make libraries that use redis use the same url (probably uneccesary)
    CACHE_REDIS_URL = RQ_REDIS_URL = REDIS_URL

    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'appname-'

class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RQ_REDIS_URL = REDIS_URL

    CACHE_TYPE = 'simple'
    # Don't do anything fancy with the assets pipeline (faster + easier to debug)
    ASSETS_DEBUG = True
    # Run jobs instantly, without needing to spin up a worker
    RQ_ASYNC = False


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    db_file = tempfile.NamedTemporaryFile()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_file.name
    SQLALCHEMY_ECHO = True

    CACHE_TYPE = 'null'
    WTF_CSRF_ENABLED = False
    RQ_ASYNC = True
