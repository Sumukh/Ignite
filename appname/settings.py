import os
import tempfile

class Config(object):
    # run flask generate_secret_key
    SECRET_KEY = os.getenv('SECRET_KEY', 'REPLACE MEasdaappnamesdas#!3de*o0alas')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Oauth config
    GOOGLE_CONSUMER_KEY = os.getenv('GOOGLE_CONSUMER_KEY', 'bad_key')
    GOOGLE_CONSUMER_SECRET = os.getenv('GOOGLE_CONSUMER_SECRET', 'bad_secret_replace_me')

    # Email Config
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.mailgun.org')
    MAIL_PORT = os.getenv('MAIL_SERVER_PORT', 2525)
    # mailers/__init__.py checks to see if this is Truthy before sending emails
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'appname <admin@appname.com>'

    SEGMENT_ANALYTICS_KEY = os.getenv('SEGMENT_ANALYTICS_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SENTRY_PUBLIC_DSN = os.getenv('SENTRY_PUBLIC_DSN')

    # Optional distinct DB value encryption key
    DB_SECRET_KEY = os.getenv('DB_ENCRYTPION_SECRET_KEY', SECRET_KEY)

    # Make libraries that use redis use the same url (probably uneccesary)
    CACHE_REDIS_URL = RQ_DASHBOARD_REDIS_URL = RQ_REDIS_URL = REDIS_URL = os.getenv(
        'REDIS_URL', 'redis://localhost:6379/0')

class ProdConfig(Config):
    ENV = 'prod'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        'sqlite:///../database.db')
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'appname-'

    # You should be using HTTPS in production anyway, but if you are not, turn
    # these two off
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'

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
    SQLALCHEMY_ECHO = False  # Optionally enable if you want to see database actions
    ASSETS_DEBUG = True

    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True
    WTF_CSRF_ENABLED = False
    RQ_ASYNC = False
