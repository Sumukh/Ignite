from flask import Blueprint, render_template, flash, abort, redirect, url_for, session
from flask_login import login_required, current_user

from appname.models.teams import Team, TeamMember
from appname.forms import SimpleForm
from appname.forms.teams import InviteMemberForm
from appname.helpers.session import current_membership

blueprint = Blueprint('dashboard_team', __name__)

@blueprint.before_request
def check_for_membership(*args, **kwargs):
    # Ensure that anyone that attempts to pull up the dashboard is currently an active member
    if not current_user.is_authenticated or current_user.primary_membership_id is None:
        flash('You currently do not have accesss to appname', 'warning')
        return redirect(url_for("main.home"))

@blueprint.route('/<hashid:team_id>/team')
@login_required
def index(team_id):
    form = InviteMemberForm()
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    return render_template('dashboard/team.html', simple_form=SimpleForm(), form=form, team=team)

@blueprint.route('/<hashid:team_id>/team/add_member', methods=['POST'])
@login_required
def add_member(team_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    form = InviteMemberForm()

    if form.validate_on_submit():
        existing_members = [member.user.email for member in team.members]
        if form.email.data not in existing_members:
            TeamMember.invite(team, form.email.data, form.role.data, current_user)
            flash('Invited {}'.format(form.email.data), 'success')
        else:
            flash('{} is already a member'.format(form.email.data), 'warning')
        return redirect(url_for('.index', team_id=team_id))
    else:
        flash('There was an error', 'warning')
        return redirect(url_for('.index', team_id=team_id))

@blueprint.route('/<hashid:team_id>/team/<hashid:invite_id>/remove_member', methods=['POST'])
@login_required
def remove_member(team_id, invite_id):
    team = Team.query.get(team_id)
    team_member = TeamMember.query.filter_by(team=team, id=invite_id).first()
    # TODO: Better permissions (can_delete?)
    if not team or not team.has_member(current_user) or not team_member:
        abort(404)

    form = SimpleForm()
    if form.validate_on_submit():
        if len(team.active_members) <= 1:
            flash('Teams must have at least one user. You cannot remove the last user', 'warning')
            return redirect(url_for('.index', team_id=team_id))

        removed_user = team_member.user or team_member.invite_email
        team_member.delete(force=True)  # Actually delete the model
        flash('Removed {}'.format(removed_user.email), 'success')
        if removed_user != current_user:
            return redirect(url_for('.index', team_id=team_id))
        else:
            return redirect(url_for('user_settings.memberships'))
    else:
        flash('There was an error', 'warning')
        return redirect(url_for('.index', team_id=team_id))