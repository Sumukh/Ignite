from flask import Blueprint, render_template, flash, redirect, url_for, Response, request
from flask_login import login_required, current_user


from appname.constants import SUPPORT_EMAIL
from appname.models import db
from appname.forms import SimpleForm
from appname.forms.login import ChangePasswordForm
from appname.forms.account import ChangeProfileForm
from appname.helpers.gdpr import GDPRExport
from appname.utils.token import generate_api_secret

from appname.extensions import stripe

settings_blueprint = Blueprint('user_settings', __name__)

@settings_blueprint.route('/settings')
@login_required
def index():
    return redirect(url_for("user_settings.account"))

@settings_blueprint.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account():
    form = ChangeProfileForm()
    return render_template('/settings/account.html', form=form)

@settings_blueprint.route('/settings/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash("Changed password", "success")
    else:
        form = ChangePasswordForm()
        return render_template('/settings/change_password.html', form=form)

@settings_blueprint.route('/settings/legal')
@login_required
def legal_compliance():
    form = SimpleForm()

    return render_template('/settings/legal_compliance.html', form=form)

@settings_blueprint.route('/settings/oauth')
@login_required
def oauth():
    return render_template('/settings/oauth.html')

@settings_blueprint.route('/settings/billing', methods=['GET', 'POST'])
@login_required
def billing():
    if request.args.get('success'):
        flash('Processing your payment', 'success')
    form = SimpleForm()

    plans = {'monthly': 'price_1HGzFQID8JASalnlgBAX2hjo',
             'annual': 'price_1HGzFQID8JASalnlBeRxlkno'}
    if form.validate_on_submit() and current_user.billing_customer_id:
        return redirect(stripe.customer_portal_link(current_user))
    return render_template('/settings/billing.html', form=form, plans=plans, stripe_publishable_key=stripe.publishable_key)


@settings_blueprint.route('/settings/api', methods=['GET', 'POST'])
@login_required
def api():
    form = SimpleForm()
    if form.validate_on_submit():
        api_key = generate_api_secret(current_user)
        current_user.hash_api_key(api_key)

        flash("Your API Key is: '{}'. It will not be displayed again, so make sure you save it.".format(api_key),
              'success')
    return render_template('/settings/api.html', form=form)

@settings_blueprint.route('/settings/memberships')
@login_required
def memberships():
    form = SimpleForm()
    memberships = current_user.memberships
    return render_template('/settings/memberships.html', form=form, memberships=memberships)

@settings_blueprint.route('/settings/legal/pii_download', methods=['POST'])
@login_required
def pii_download():
    form = SimpleForm()

    if form.validate_on_submit():
        return Response(GDPRExport(current_user, current_user).export_user_pii_json(),
                        mimetype='application/json',
                        headers={'Content-Disposition': 'attachment;filename=user-export.json'})
    else:
        flash('Please try submitting the form again', 'warning')

    return redirect(url_for("user_settings.legal_compliance"))

@settings_blueprint.route('/settings/legal/pii_send_export', methods=['POST'])
@login_required
def pii_notification():
    # Should be queued as a job
    form = SimpleForm()
    if form.validate_on_submit():
        GDPRExport(current_user, current_user).send_pii_export()
        flash("Export queued & will be sent to your email", 'success')
    else:
        flash('Please try submitting the form again', 'warning')
    return redirect(url_for("user_settings.legal_compliance"))

@settings_blueprint.route('/settings/legal/account_deletion', methods=['POST'])
@login_required
def account_deletion():
    form = SimpleForm()
    if form.validate_on_submit():
        # TODO: Actual deletion scheduling
        flash("Please email {0} to delete your account".format(SUPPORT_EMAIL), 'warning')
    else:
        flash('Please try submitting the form again', 'warning')
    return redirect(url_for("user_settings.legal_compliance"))
