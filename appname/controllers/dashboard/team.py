from flask_login import login_required, current_user

from flask import (Blueprint, render_template, flash, abort,
                   redirect, url_for, session, Markup)

from appname.constants import REQUIRE_EMAIL_CONFIRMATION
from appname.models import db
from appname.models.teams import Team, TeamMember
from appname.forms import SimpleForm
from appname.forms.teams import InviteMemberForm
from appname.helpers.session import current_membership

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
    form = InviteMemberForm()
    membership = current_membership()
    team = membership.team
    return render_template('dashboard/team.html', simple_form=SimpleForm(), form=form, team=team)

@blueprint.route('/team/<hashid:team_id>/add_member', methods=['POST'])
@login_required
def add_member(team_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    form = InviteMemberForm()
    if form.validate_on_submit():
        TeamMember.invite(team, form.email.data, form.role.data, current_user)
        flash('Invited {}'.format(form.email.data), 'success')
        return redirect(url_for('.index'))
    else:
        flash('There was an error', 'warning')
        return redirect(url_for('.index'))

@blueprint.route('/team/<hashid:team_id>/<hashid:invite_id>/remove_member', methods=['POST'])
@login_required
def remove_member(team_id, invite_id):
    team = Team.query.get(team_id)
    team_member = TeamMember.query.filter_by(team=team, id=invite_id).first()
    # TODO: Better permissions (can_delete?)
    if not team or not team.has_member(current_user) or not team_member:
        abort(404)

    form = SimpleForm()
    if form.validate_on_submit():
        removed_user = team_member.user or team_member.invite_email
        team_member.delete(force=True) # Actually delete the model
        flash('Removed {}'.format(removed_user), 'success')
        return redirect(url_for('.index'))
    else:
        flash('There was an error', 'warning')
        return redirect(url_for('.index'))

