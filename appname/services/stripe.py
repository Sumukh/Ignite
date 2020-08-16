from flask import url_for
import stripe

class Stripe:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        stripe_key = app.config.get('STRIPE_SECRET_KEY')

        stripe.publishable_key = app.config.get('STRIPE_PUBLISHABLE_KEY')
        stripe.api_key = stripe_key

        if app.debug:
            stripe.verify_ssl_certs = False

    def customer_portal_link(self, user, return_url=None):
        data = stripe.billing_portal.Session.create(
            customer='cus_HqbkOnBTRiG9Uq',
            return_url=url_for('user_settings.billing', _external=True),
        )
        return data['url']
