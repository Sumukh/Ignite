from flask_login import login_required, current_user

from flask import Blueprint, render_template, flash, redirect, url_for, session, Markup

from appname.constants import REQUIRE_EMAIL_CONFIRMATION
from appname.models import db
from appname.models.teams import Team
from appname.forms.login import ChangePasswordForm
from appname.helpers.session import current_membership

blueprint = Blueprint('dashboard_home', __name__)

@blueprint.route('/')
@login_required
def index():
    return render_template('dashboard/home.html')
    # todo: Lookup in session or do a default redirect.
    return redirect(url_for('.home', team_id=current_user.active_memberships[0].team.id))

@blueprint.route('/<hashid:team_id>')
@login_required
def home(team_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    return render_template('dashboard/home.html', team=team)
