from flask_login import login_required, current_user

from flask import Blueprint, render_template, flash, redirect, url_for, session, Markup

from appname.constants import REQUIRE_EMAIL_CONFIRMATION
from appname.models import db
from appname.forms.login import ChangePasswordForm
from appname.utils.session import current_membership

blueprint = Blueprint('dashboard_team', __name__)

@blueprint.before_request
def check_for_membership(*args, **kwargs):
    # Ensure that anyone that attempts to pull up the dashboard is currently an active member
    if current_user.primary_membership_id is None:
        flash('You currently do not have accesss to appname', 'warning')
        return redirect(url_for("main.home"))

@blueprint.route('/team')
@login_required
def index():
    form = ChangePasswordForm()
    membership = current_membership()
    team = membership.team
    return render_template('dashboard/team.html', form=form, team=team)
