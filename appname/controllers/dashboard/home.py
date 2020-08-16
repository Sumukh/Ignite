from flask import Blueprint, render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from appname.models.teams import Team

blueprint = Blueprint('dashboard_home', __name__)

@blueprint.route('/')
@login_required
def index():
    if current_user.active_memberships:
        return redirect(url_for('.home', team_id=current_user.active_memberships[0].team.id))
    else:
        flash("You are not part of any teams", 'warning')
        return redirect(url_for('user_settings.memberships'))

@blueprint.route('/<hashid:team_id>')
@login_required
def home(team_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    return render_template('dashboard/home.html', team=team)
