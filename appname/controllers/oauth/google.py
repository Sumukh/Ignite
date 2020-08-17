    # API
from flask import flash
from flask_login import current_user, login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound

from appname.models import db
from appname.extensions import cache
from appname.models.user import User, OAuth


blueprint = make_google_blueprint(
    scope=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
           "openid"],
    storage=SQLAlchemyStorage(OAuth, db.session, user=lambda: current_user, cache=cache),
)

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="warning")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="warning")
        return False

    google_info = resp.json()
    google_user_id = google_info["id"]

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name, provider_user_id=google_user_id
    )
    try:
        oauth = query.one()
    except NoResultFound:
        google_user_login = str(google_info["email"])
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            provider_user_login=google_user_login,
            token=token,
        )

    existing_user = User.lookup(google_info["email"])
    # Since google verifies their primary emails, we can be more assured that we can directly login a user.

    if oauth.user:
        login_user(oauth.user)
        flash("Welcome back.", 'success')
    elif current_user.is_authenticated and current_user.email == google_info["email"]:
        oauth.user = current_user
        db.session.add(oauth)
        db.session.commit()
        flash("Successfully linked Google account.", 'success')
    elif existing_user and existing_user.email == google_info['email']:
        oauth.user = existing_user
        db.session.add(oauth)
        db.session.commit()
        login_user(existing_user)
        flash("Successfully signed in as {}".format(existing_user.email), 'success')
    else:
        # Create a new local user account for this user
        user = User(email=google_info["email"], name=google_info["name"],
                    email_confirmed=google_info["verified_email"])
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Welcome to appname!", 'success')

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")
