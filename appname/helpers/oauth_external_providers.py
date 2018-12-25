# This file lists OAuth configurations for popular providers
# See Flask-OAuthlib documentation for more
import datetime as dt
import logging

from werkzeug import security
from flask import session, flash, redirect, request
from flask_oauthlib.client import OAuthException

from appname.models import db
from appname.models.user import User

logger = logging.getLogger(__name__)

class ExternalProviderException(Exception):
    pass

class BaseProvider:
    base_config = {}

    def __init__(self):
        self.config = self.base_config.copy()

    @property
    def name(self):
        """ Convert Twitter to TWITTER """
        return self.__class__.__name__.upper()

    @staticmethod
    def get_token():
        return session.get('provider_token')

    def init_app(self, app, oauth):
        # Set consumer key/secret from class_name
        key = app.config.get('{}_CONSUMER_KEY'.format(self.name),
                             'example')
        secret = app.config.get('{}_CONSUMER_SECRET'.format(self.name),
                                'example')

        self.config['consumer_key'] = key
        self.config['consumer_secret'] = secret

        self.client = oauth.remote_app(
            self.name,
            **self.config
        )
        self.client.tokengetter(self.get_token)

    def parse_repsonse(self, resp):
        # Parse the oauth response from the provider
        access_token = resp['access_token']
        expires_in = resp.get('expires_in', 0)
        session['token_expiry'] = dt.datetime.now() + dt.timedelta(seconds=expires_in)
        session['provider_token'] = (access_token, '')  # (access_token, secret)

    def authorized_repsonse(self):
        try:
            resp = self.client.authorized_response()
        except OAuthException as e:
            title = e.data.get('error', 'Unknown Error')
            description = e.data.get('error_description', 'Unknown')
            error = "{0} - Reason: {1}. Try again".format(title, description)
            flash(error, "danger")
            # TODO Error Page
            return redirect("/")
        if resp is None:
            error = "Access denied: reason={0} error={1}".format(
                request.args['error_reason'],
                request.args['error_description']
            )
            flash(error, "danger")
            # TODO Error Page
            return redirect("/")
        return self.parse_repsonse(resp)

    def find_user_by_email(self, email, email_confirmed_by_provider=False):
        if not email:
            raise ExternalProviderException("We were unable to associate that login with an account")

        # Allowing an unverified email to log on is a security risk since someone else may
        # have setup an "unconfirmed" account on the external provider for one of our users
        if not email_confirmed_by_provider:
            raise ExternalProviderException(
                "Please verify your email on {} first".format(
                    self.__class__.__name__))

        user = User.lookup_or_create_by_email(email, email_confirmed=True)
        if not user.email_confirmed:
            user.email_confirmed = True
            db.session.add(user)
            db.session.commit()
        return user

class Twitter(BaseProvider):

    base_config = {
        'base_url': 'https://api.twitter.com/1.1/',
        'request_token_url': 'https://api.twitter.com/oauth/request_token',
        'access_token_method': 'POST',
        'access_token_url': 'https://api.twitter.com/oauth/access_token',
        'authorize_url': 'https://api.twitter.com/oauth/authorize'
    }

    def get_user(self, token):
        response = self.client.get('user', token=token)
        # You need special access to get a users email from Twitter...
        # See: https://stackoverflow.com/a/32852370
        if response.status != 200:
            logger.warning("Error {}".format(response.data))
            raise ExternalProviderException("Unknown Twitter Error when logging in")
        user_data = response.data
        email = user_data['data']['email']
        # Twitter should return null if their email is not confirmed
        return self.find_user_by_email(email, email_confirmed_by_provider=True)

    def parse_repsonse(self, resp):
        access_token = resp['oauth_token']
        token_secret = resp['oauth_token_secret']

        expires_in = int(resp.get('x_auth_expires', 0))
        session['token_expiry'] = dt.datetime.now() + dt.timedelta(seconds=expires_in)
        session['provider_token'] = (access_token, token_secret)  # (access_token, secret)
        # Extras
        session['twitter_screen_name'] = resp['screen_name']
        return session['provider_token']

class Google(BaseProvider):
    base_config = {
        'request_token_params': {
            'scope': 'email',
            'state': lambda: security.gen_salt(10),
            'prompt': 'select_account'  # (optional) forces google to show the account selector
        },
        'base_url': 'https://www.googleapis.com/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'authorize_url': 'https://accounts.google.com/o/oauth2/v2/auth'
    }

    def get_user(self, token):
        response = self.client.get('oauth2/v3/userinfo')
        user_data = response.data or {}
        if response.status != 200 or 'error' in user_data:
            logger.warning("Error {} {}".format(response.status, user_data))
            raise ExternalProviderException("There was an unexpected error when logging you in")
        email_confirmed = user_data.get('email_verified') or user_data.get('verified_email')
        return self.find_user_by_email(user_data.get("email"), email_confirmed)

class Okpy(BaseProvider):

    base_config = {
        'request_token_params': {'scope': 'email',
                                 'state': lambda: security.gen_salt(10)},
        'base_url': 'https://okpy.org/api/v3/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://okpy.org/oauth/token',
        'authorize_url': 'https://okpy.org/oauth/authorize'
    }

    def get_user(self, token):
        response = self.client.get('user', token=token)
        if response.status != 200:
            raise ExternalProviderException("There was an unexpected error when logging you in")
        user_data = response.data
        email = user_data['data']['email']
        # We trust okpy's authentication/confirmation since they only use OAuth
        return self.find_user_by_email(email, True)
