from flask import Blueprint, render_template, flash, request, redirect, url_for, session, abort
from flask_login import login_user, logout_user, login_required, current_user

import appname.constants as constants

from appname.forms.login import LoginForm, SimpleForm
from appname.models import db
from appname.models.user import User
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
    elif request.method == 'POST':
        flash("That login did not work", "warning")

    return render_template("auth/login.html", form=form)

@auth.route("/auth/logout")
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))

