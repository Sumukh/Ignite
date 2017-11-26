from flask import Blueprint, render_template, flash, request, redirect, url_for, session, abort
from flask_login import login_user, logout_user, login_required, current_user

import appname.constants as constants

from appname.forms.login import LoginForm, SignupForm, SimpleForm, RequestPasswordResetForm, ChangePasswordForm
from appname.models import db
from appname.models.user import User
from appname.mailers.auth import ConfirmEmail, ResetPassword
from appname.extensions import login_manager, token, limiter

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

@login_manager.unauthorized_handler
def unauthorized():
    session['after_login'] = request.url
    login_hint = request.args.get('login_hint')
    return redirect(url_for('auth.login', login_hint=login_hint))

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for("main.home"))

    return render_template("login.html", form=form)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        user = User(form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)

        if constants.REQUIRE_EMAIL_CONFIRMATION:
            # Send confirm email
            ConfirmEmail(user).send()

        flash("Welcome to appname.", "success")
        return redirect(request.args.get("next") or url_for("dashboard.home"))

    return render_template("signup.html", form=form)

@auth.route("/auth/logout")
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))

@auth.route("/confirm/<string:code>")
def confirm(code):
    if not constants.REQUIRE_EMAIL_CONFIRMATION:
        abort(404)

    try:
        email = token.decode(code, salt=EMAIL_CONFIRMATION_SALT)
    except Exception as e:
        email = None

    if not email:
        # TODO: Render a nice error page here.
        return abort(404)

    user = User.query.filter_by(email=email).first()
    if not user:
        return abort(404)
    user.email_confirmed = True
    db.session.commit()

    if current_user == user:
        flash('Succesfully confirmed your email', 'success')
        return redirect(url_for("dashboard.home"))
    else:
        flash('Confirmed your email. Please login to continue', 'success')
        return redirect(url_for("auth.login"))


@auth.route("/auth/resend-confirmation", methods=["GET", "POST"])
@limiter.limit("5/minute")
@login_required
def resend_confirmation():
    if not constants.REQUIRE_EMAIL_CONFIRMATION:
        abort(404)
    if current_user.email_confirmed:
        return redirect(url_for("dashboard.home"))

    form = SimpleForm()
    if form.validate_on_submit():
        if ConfirmEmail(current_user).send():
            flash("Sent confirmation to {}".format(current_user.email), 'success')
        return redirect(url_for("dashboard.home"))

    return render_template('auth/resend_confirmation.html', form=form)

@auth.route("/auth/reset_password", methods=["GET", "POST"])
@limiter.limit("10/minute;20/hour")
def request_password_reset():
    if not current_user.is_anonymous:
        flash('You must be logged out to reset your password', 'warning')
        return redirect(url_for("dashboard.home"))
    form = RequestPasswordResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        if user:
            ResetPassword(user).send()
            flash("We sent you a password reset email.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Hmm. That email doesn't appear to be registered ", "success")
    return render_template("auth/request_password_reset.html", form=form)

@auth.route("/auth/reset_password/<string:code>", methods=["GET", "POST"])
def reset_password(code):
    if not current_user.is_anonymous:
        flash('You must be logged out to reset your password', 'warning')
        return redirect(url_for("dashboard.home"))

    try:
        email = token.decode(code, salt=constants.PASSWORD_RESET_SALT)
    except Exception as e:
        email = None

    if not email:
        return abort(403)

    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).one()
        user.password = form.password.data
        db.session.commit()
        login_user(user)

        flash("Changed your password succesfully", "success")
        return redirect(request.args.get("next") or url_for("dashboard.home"))

    return render_template("auth/reset_password.html", form=form)


@auth.route("/reauth", methods=["GET", "POST"])
def reauth():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        login_user(user)

        flash("Re-authenticated successfully.", "success")
        return redirect(request.args.get("next") or url_for("dashboard.settings"))

    return render_template("reauth.html", form=form)
