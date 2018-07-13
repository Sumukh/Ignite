from flask_login import login_required, current_user

from flask import Blueprint, render_template, flash, redirect, url_for, session, Markup

from appname.constants import REQUIRE_EMAIL_CONFIRMATION
from appname.models import db
from appname.forms.login import ChangePasswordForm
from appname.utils.session import current_membership

blueprint = Blueprint('dashboard_settings', __name__)

@blueprint.before_request
def check_for_membership(*args, **kwargs):
    # Ensure that anyone that attempts to pull up the dashboard is currently an active member
    if current_user.primary_membership_id is None:
        flash('You currently do not have accesss to appname', 'warning')
        return redirect(url_for("main.home"))

@blueprint.route('/settings')
@login_required
def index():
    # TODO: Implement @fresh_login_required for non-oauthed users (users with a password)
    form = ChangePasswordForm()
    return render_template('dashboard/settings.html', form=form)

@blueprint.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash("Changed password", "success")
    else:
        flash("The password was invalid", "warning")

    return redirect(url_for("dashboard_settings.index"))
