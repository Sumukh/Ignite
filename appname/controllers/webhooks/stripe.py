from flask import Blueprint, request, url_for, abort

from appname.models.user import User
from appname.extensions import csrf, stripe

stripe_blueprint = Blueprint('checkout', __name__)

@stripe_blueprint.route('/stripe', methods=['POST'])
@csrf.exempt  # Because this request is coming over an external API
def stripe_webhook():
    event = stripe.parse_webhook(request.data.decode("utf-8"), request.headers)
    print(event)
    print(event['data']['object'])
    if event.type == 'customer.subscription.deleted':
        subscription = event['data']['object']
    elif event.type == 'customer.subscription.created':
        subscription = event['data']['object']
        status = subscription['status']
        metadata = subscription['metadata']
        # Find your team or user and change their plan status to premium
        if status == 'active':
            pass
    elif event.type == 'customer.subscription.updated':
        # Upgrades and downgrades.
        pass
    elif event.type == 'checkout.session.completed':
        pass

    # Parse and handle events here.
    return "OK", 200
