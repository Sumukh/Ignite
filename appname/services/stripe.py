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
