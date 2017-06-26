""" OAuth client for logging in with external accounts.
"""
from flask import Blueprint, flash, request, redirect, url_for, session
from flask_login import login_user
from flask_oauthlib.client import OAuth, OAuthException

from appname.controllers.oauth import external_providers

oauth_client = Blueprint('oauth_client', __name__)

oauth = OAuth()

# Change this value to change providers
external_provider = external_providers.Twitter()

@oauth_client.record
def record_params(setup_state):
    """ Load used app configs into local config on registration from
    server/__init__.py and sets up the OAuth client."""
    app = setup_state.app
    oauth.init_app(app)
    # Repeated calls of record_parms should not crash oauthlib.
    if not hasattr(external_provider, 'client'):
        external_provider.init_app(app, oauth)

@oauth_client.route("/login/")
def login():
    """
    Authenticates a user with an access token from the service
    """
    return external_provider.client.authorize(
        callback=url_for('.authorized', _external=True),
        login_hint=request.args.get('login_hint'))

@oauth_client.route('/login/authorized/')
def authorized():
    # Set session variables from response
    token = external_provider.authorized_repsonse()
    user = external_provider.get_user(token)
    if not user:
        flash("We could not log you in. Try again soon", 'warning')
        return redirect('/')

    login_user(user)
    after_login = session.pop('after_login', None)
    return redirect(after_login or url_for('main.home'))
