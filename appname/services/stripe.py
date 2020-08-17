from urllib.parse import unquote

from flask import url_for
from appname.models import db

import stripe

class Stripe:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        stripe_key = app.config.get('STRIPE_SECRET_KEY')
        self.publishable_key = app.config.get('STRIPE_PUBLISHABLE_KEY')
        self.webhook_key = app.config.get('STRIPE_WEBHOOK_KEY')

        stripe.publishable_key = self.publishable_key
        stripe.api_key = stripe_key

        if app.debug:
            stripe.verify_ssl_certs = False

    def get_customer(self, customer_id):
        return stripe.Customer.retrieve(customer_id)

    def create_customer(self, user):
        if user.billing_customer_id:
            return user.billing_customer_id
        stripe_customer = stripe.Customer.create(name=user.full_name, email=user.email)

        user.billing_customer_id = stripe_customer.id
        db.session.add(user)
        db.session.commit()
        return stripe_customer.id

    def create_session(self, user):
        session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    mode='subscription',
                    )
        return session



    def customer_portal_link(self, user, return_url=None):
        if not user.billing_customer_id:
            return

        data = stripe.billing_portal.Session.create(
            customer=user.billing_customer_id,
            return_url=url_for('user_settings.billing', _external=True),
        )
        return data['url']

    def parse_webhook(self, payload, headers):
        received_sig = headers.get("Stripe-Signature", None)
        # This will raise an exception if it's invalid
        return stripe.Webhook.construct_event(
            payload, received_sig, self.webhook_key
        )

