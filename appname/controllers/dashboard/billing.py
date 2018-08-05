from flask_login import login_required, current_user

from flask import (Blueprint, render_template, flash, abort,
                   redirect, url_for, session, Markup)

from appname.models import db
from appname.models.teams import Team
from appname.models.billing import ProductPlan, StripeSubscription
from appname.forms import SimpleForm
from appname.utils.session import current_membership

blueprint = Blueprint('dashboard_billing', __name__)

@blueprint.before_request
def check_for_membership(*args, **kwargs):
    # Ensure that anyone that attempts to pull up the dashboard is currently an active member
    if current_user.primary_membership_id is None:
        flash('You currently do not have accesss to appname', 'warning')
        return redirect(url_for("main.home"))

@blueprint.route('/<hashid:team_id>/billing')
@login_required
def index(team_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    subscription = team.subscription
    available_plans = ProductPlan.query.filter_by(public=True).all()

    return render_template('dashboard/billing.html', simple_form=SimpleForm(),
                           team=team, subscription=subscription, plans=available_plans)

@blueprint.route('/<hashid:team_id>/billing/upgrade', methods=['POST'])
@login_required
def change_plan(team_id):
    team = Team.query.get(team_id)
    if not team or not team.has_member(current_user):
        abort(404)
    return render_template('dashboard/billing.html', simple_form=SimpleForm(), team=team)
