from flask_login import login_required, current_user

from flask import Blueprint, render_template, flash, redirect, url_for, session, Markup, Response

from appname.constants import REQUIRE_EMAIL_CONFIRMATION, SUPPORT_EMAIL
from appname.models import db
from appname.forms import SimpleForm
from appname.forms.login import ChangePasswordForm
from appname.forms.account import ChangeProfileForm
from appname.helpers.gdpr import GDPRExport
from appname.helpers.session import current_membership

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
    return redirect(url_for("dashboard_settings.account"))

@blueprint.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account():
    form = ChangeProfileForm()
    return render_template('dashboard/settings/account.html', form=form)

@blueprint.route('/settings/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash("Changed password", "success")
    else:
        form = ChangePasswordForm()
        return render_template('dashboard/settings/change_password.html', form=form)

@blueprint.route('/settings/legal')
@login_required
def legal_compliance():
    form = SimpleForm()

    return render_template('dashboard/settings/legal_compliance.html', form=form)

@blueprint.route('/settings/legal/pii_download', methods=['POST'])
@login_required
def pii_download():
    form = SimpleForm()

    if form.validate_on_submit():
        return Response(GDPRExport(current_user, current_user).export_user_pii_json(),
                        mimetype='application/json',
                        headers={'Content-Disposition': 'attachment;filename=user-export.json'})
    else:
        flash('Please try submitting the form again', 'warning')

    return redirect(url_for("dashboard_settings.legal_compliance"))

@blueprint.route('/settings/legal/pii_send_export', methods=['POST'])
@login_required
def pii_notification():
    # Should be queued as a job
    form = SimpleForm()
    if form.validate_on_submit():
        GDPRExport(current_user, current_user).send_pii_export()
        flash("Export queued & will be sent to your email", 'success')
    else:
        flash('Please try submitting the form again', 'warning')
    return redirect(url_for("dashboard_settings.legal_compliance"))

@blueprint.route('/settings/legal/account_deletion', methods=['POST'])
@login_required
def account_deletion():
    form = SimpleForm()
    if form.validate_on_submit():
        # TODO: Actual deletion scheduling
        flash("Please email {0} to delete your account".format(SUPPORT_EMAIL), 'warning')
    else:
        flash('Please try submitting the form again', 'warning')
    return redirect(url_for("dashboard_settings.legal_compliance"))

@blueprint.route('/settings/notifications')
@login_required
def notifications():
    return render_template('dashboard/settings/notifications.html')

