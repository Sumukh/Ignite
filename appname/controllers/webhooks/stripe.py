from itertools import product
import logging
from flask import Blueprint, request, url_for, abort

from appname.models import db
from appname.models.user import User
from appname.models.teams import Team
from appname.extensions import csrf, stripe
from appname.billing_plans import plans_by_price_id, MonthlyPremium

stripe_blueprint = Blueprint('checkout', __name__)

logger = logging.getLogger(__name__)



@stripe_blueprint.route('/stripe', methods=['POST'])
@csrf.exempt  # Because this request is coming over an external API
def stripe_webhook():
    event = stripe.parse_webhook(request.data.decode("utf-8"), request.headers)
    # TODO: Make this into a service object and move this logic out.
    # TODO: Code is messy but this logic will likely need to be customized for each user.

    if event.type == 'customer.subscription.deleted':
        subscription = event['data']['object']
        team = Team.query.filter_by(subscription_id=subscription['id']).first()
        team.plan = 'free'
        db.session.add(team)
        db.session.commit()
    elif event.type == 'customer.subscription.created':
        subscription = event['data']['object']
        plan = subscription['plan']
        status = subscription['status']
        team = Team.query.filter_by(subscription_id=subscription['id']).first()
        team.billing_customer_id = subscription["customer"]
        # TODO: Confusing ID / Lookup
        price_id = plan["id"]
        # Customize to however you do your billing plan logic (or lookup the plan name)
        team.plan = plans_by_price_id.get(price_id) or MonthlyPremium.name
        db.session.add(team)
        db.session.commit()
    elif event.type == 'customer.subscription.updated':
        # Upgrades and downgrades.
        subscription = event['data']['object']
        status = subscription['status']
        if status == 'cancelled' or status == 'unpaid':
            # find the sub and donwgrade the plan
            team = Team.query.filter_by(subscription_id=subscription['id']).first()
            team.plan = 'free' # Customize to whatever you want (or lookup the plan name)
            db.session.add(team)
            db.session.commit()
    elif event.type == 'checkout.session.completed':
        # Once checkout for single item and subscription is done
        # Store the subscription on the team
        checkout = event['data']['object']
        if checkout["subscription"]:
            team_id = checkout["client_reference_id"]
            team = Team.query.get(team_id)
            if not team:
                # Log and error
                logger.info("Unknown reference id")
                return "?", 200
            team.subscription_id = checkout["subscription"]
            team.billing_customer_id = checkout["customer"]
            db.session.add(team)
            db.session.commit()

    # Parse and handle events here.
    return "OK", 200
