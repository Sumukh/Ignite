""" OAuth client for logging in with external accounts.
"""
import datetime as dt

from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from flask_login import login_user
from flask_oauthlib.client import OAuth, OAuthException
from werkzeug import security

from appname.forms.login import LoginForm
from appname.models.user import User
from appname.extensions import login_manager

oauth_client = Blueprint('oauth_client', __name__)

oauth = OAuth()

@oauth_client.record
def record_params(setup_state):
    """ Load used app configs into local config on registration from
    server/__init__.py """
    app = setup_state.app
    oauth.init_app(app)

provider_auth = oauth.remote_app(
    'ok-server',  # Server Name
    consumer_key='example',
    consumer_secret='your-secret-here',
    request_token_params={'scope': 'email',
                          'state': lambda: security.gen_salt(10)},
    base_url='https://okpy.org/api/v3/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://okpy.org/oauth/token',
    authorize_url='https://okpy.org/oauth/authorize'
)

def user_from_token(token):
    # Make a request to base_url/user to get user_info
    response = provider_auth.get('user')
    if response.status == 200:
        user_data = response.data
        email = user_data['data']['email']
        return User.lookup_or_create(email)
    else:
        flash("We could not log you in. Try again soon", 'warning')
        return redirect('/')

@provider_auth.tokengetter
def get_provider_token(token=None):
    return session.get('provider_token')

@oauth_client.route("/login/")
def login():
    """
    Authenticates a user with an access token using Google APIs.
    """
    return provider_auth.authorize(
        callback=url_for('.authorized', _external=True),
        login_hint=request.args.get('login_hint'))



@oauth_client.route('/login/authorized/')
def authorized():
    try:
        resp = provider_auth.authorized_response()
    except OAuthException as e:
        error = "{0} - Reason: {1}. Try again".format(e.data.get('error', 'Unknown Error'),
                                           e.data.get('error_description', 'Unknown'))
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

    access_token = resp['access_token']

    expires_in = resp.get('expires_in', 0)
    session['token_expiry'] = dt.datetime.now() + dt.timedelta(seconds=expires_in)
    session['provider_token'] = (access_token, '')  # (access_token, secret)
    user = user_from_token(access_token)

    login_user(user)
    after_login = session.pop('after_login', None)
    return redirect(after_login or url_for('main.home'))
