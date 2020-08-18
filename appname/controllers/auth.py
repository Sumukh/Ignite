from flask import Blueprint, render_template, flash, request, redirect, url_for, session, abort
from flask_login import login_user, logout_user, login_required, current_user

import appname.constants as constants

from appname.forms import SimpleForm
from appname.forms.login import LoginForm, SignupForm, RequestPasswordResetForm, ChangePasswordForm
from appname.models import db
from appname.models.user import User
from appname.models.teams import TeamMember
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
@limiter.limit("20/minute")
def login():
    if not constants.ALLOW_PASSWORD_LOGIN:
        return render_template("auth/oauth_only_login.html")

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        session['current_team_membership_id'] = user.primary_membership_id
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for("main.home"))

    return render_template("auth/login.html", form=form)

@auth.route("/signup", methods=["GET", "POST"])
@limiter.limit("10/minute")
def signup():
    if not constants.ALLOW_SIGNUPS:
        return abort(404)

    form = SignupForm(invite_secret=request.args.get('invite_secret'))

    if form.validate_on_submit():
        team_secret = form.invite_secret.data
        invite = (TeamMember.query.filter_by(invite_secret=team_secret, activated=False)
                            .one_or_none())

        if invite:
            user = User(form.email.data, form.password.data,
                        email_confirmed=True, team=invite.team)
            invite.user = user
            db.session.add(invite)
        else:
            user = User(form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        session['current_team_membership_id'] = user.primary_membership_id
        login_user(user)

        if constants.REQUIRE_EMAIL_CONFIRMATION:
            # Send confirm email
            ConfirmEmail(user).send()

        flash("Welcome to appname.", "success")
        return redirect(request.args.get("next") or url_for("dashboard_home.index"))

    return render_template("auth/signup.html", form=form, invite_secret=request.args.get('invite_secret'))

@auth.route("/auth/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.home"))

@auth.route("/confirm/<string:code>")
def confirm(code):
    if not constants.REQUIRE_EMAIL_CONFIRMATION:
        abort(404)

    try:
        email = token.decode(code, salt=constants.EMAIL_CONFIRMATION_SALT)
    except Exception:
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
        return redirect(url_for("dashboard_home.index"))
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
        return redirect(url_for("dashboard_home.index"))

    form = SimpleForm()
    if form.validate_on_submit():
        if ConfirmEmail(current_user).send():
            flash(
                "Sent confirmation to {}".format(
                    current_user.email),
                'success')
        return redirect(url_for("dashboard_home.index"))

    return render_template('auth/resend_confirmation.html', form=form)

@auth.route("/auth/reset_password", methods=["GET", "POST"])
@limiter.limit("20/hour")
def request_password_reset():
    if not current_user.is_anonymous:
        flash('You must be logged out to reset your password', 'warning')
        return redirect(url_for("dashboard_home.index"))
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
@limiter.limit("20/hour")
def reset_password(code):
    if not current_user.is_anonymous:
        flash('You must be logged out to reset your password', 'warning')
        return redirect(url_for("dashboard_home.index"))

    try:
        email = token.decode(code, salt=constants.PASSWORD_RESET_SALT)
    except Exception:
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
        return redirect(request.args.get("next") or url_for("dashboard_home.index"))

    return render_template("auth/reset_password.html", form=form)


@auth.route("/reauth", methods=["GET", "POST"])
def reauth():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
        login_user(user)

        flash("Re-authenticated successfully.", "success")
        return redirect(request.args.get("next", url_for("user_settings.index")))
    return render_template("reauth.html", form=form)

@auth.route('/invite/<hashid:invite_id>/join')
@login_required
def join_team(invite_id):
    invite = TeamMember.query.get(invite_id)
    if not invite or invite.user != current_user:
        return abort(404)

    invite.activate(current_user.id)
    return redirect(url_for("dashboard_home.index"))

@auth.route('/join/<hashid:invite_id>/<string:secret>')
@limiter.limit("20/minute")
def invite_page(invite_id, secret):
    invite = TeamMember.query.get(invite_id)
    if not invite.invite_secret or invite.invite_secret != secret or invite.activated:
        return abort(404)

    if current_user.is_authenticated and invite.user == current_user:
        return redirect(url_for(".join_team", invite_id=invite.id))

    form = SignupForm(invite_secret=invite.invite_secret)
    return render_template("auth/invite.html", form=form, invite=invite)

