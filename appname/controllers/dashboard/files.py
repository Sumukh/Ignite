from flask import Blueprint, render_template, flash, abort, redirect, request, url_for, session
from flask_login import login_required, current_user

from appname.extensions import storage
from appname.models import db
from appname.models.teams import Team, TeamMember
from appname.models.team_file import TeamFile
from appname.forms import SimpleForm
from appname.forms.files import FileForm
from appname.helpers.session import current_membership

blueprint = Blueprint('dashboard_files', __name__)

@blueprint.before_request
def check_for_membership(*args, **kwargs):
    # Ensure that anyone that attempts to pull up the dashboard is currently belongs to any team on our site
    if not current_user.is_authenticated or current_user.primary_membership_id is None:
        flash('You currently do not have accesss to appname', 'warning')
        return redirect(url_for("main.home"))

@blueprint.route('/<hashid:team_id>/files')
@login_required
def index(team_id):
    form = FileForm()
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    return render_template('dashboard/files.html', form=form, files=team.files, team=team)

@blueprint.route('/<hashid:team_id>/files/add_file', methods=['POST'])
@login_required
def add_file(team_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    form = FileForm()

    if form.validate_on_submit():
        attachment = storage.upload(form.attachment.data)

        team_file = TeamFile(team=team, user=current_user, description=form.description.data,
                             file_name=attachment.info['name'],
                             file_object_name=attachment.name)
        db.session.add(team_file)
        db.session.commit()

        flash("Succesfully Uploaded {}".format(team_file.file_name, attachment.url), 'warning')
        return redirect(url_for('.index', team_id=team_id))

@blueprint.route('/<hashid:team_id>/files/<hashid:file_id>')
@login_required
def download_file(team_id, file_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    team_file = TeamFile.query.filter_by(team=team, id=file_id).one()
    if team_file:
        file_object = storage.get(team_file.file_object_name)
        # Instead of redirecting, you can use the save to URL
        if file_object:
            return redirect(file_object.download_url())
    return abort(404)

@blueprint.route('/<hashid:team_id>/files/<hashid:file_id>/destroy', methods=['POST'])
@login_required
def destroy_file(team_id, file_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    team_file = TeamFile.query.filter_by(team=team, id=file_id).one()
    if team_file:
        file_object = storage.get(team_file.file_object_name)
        db.session.delete(team_file)
        db.session.commit()
        if file_object:
            file_object.delete()
        return redirect(url_for('.index', team_id=team.id))
    return abort(404)
