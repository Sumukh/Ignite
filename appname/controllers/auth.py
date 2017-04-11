from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from flask_login import login_user, logout_user

from appname.forms.login import LoginForm
from appname.models.user import User
from appname.extensions import login_manager

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

@login_manager.unauthorized_handler
def unauthorized():
    session['after_login'] = request.url
    login_hint = request.args.get('login_hint')
    return redirect(url_for('.login', login_hint=login_hint))

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for("main.home"))

    return render_template("login.html", form=form)

@auth.route("/logout")
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))

