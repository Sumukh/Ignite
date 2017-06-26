# This file lists OAuth configurations for popular providers
# See Flask-OAuthlib documentation for more
import datetime as dt

from werkzeug import security
from flask import session

from appname.models.user import User

class BaseProvider:
    base_config = {}

    def __init__(self):
        self.config = self.base_config.copy()

    @property
    def name(self):
        # Convert Twitters -> TWITTER
        return self.__class__.__name__.upper()

    @staticmethod
    def get_token(token):
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
        if response.status == 200:
            user_data = response.data
            email = user_data['data']['email']
            return User.lookup_or_create(email)

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
            'prompt': 'select_account'
        },
        'base_url': 'https://www.googleapis.com/plus/v1/',
        'request_token_url': None,
        'access_token_method': 'POST',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth'
    }

    def get_user(self, token):
        response = self.client.get('people/me')
        if response.status == 200:
            user_data = response.data
            if 'error' not in user_data and user_data.get('emails'):
                email = user_data['emails'][0]['value']
                return User.lookup_or_create(email)

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
        if response.status == 200:
            user_data = response.data
            email = user_data['data']['email']
            return User.lookup_or_create(email)

