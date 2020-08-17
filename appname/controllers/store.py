import stripe

from flask import Blueprint, flash, render_template, request

from appname.models.user import User
from appname.extensions import csrf

from appname.mailers.store import PurchaseReceipt

store = Blueprint('store', __name__)

@store.route('/store')
def home():
    return render_template('store/product.html', stripe_publishable_key=stripe.publishable_key)


@store.route('/store/payment', methods=['POST'])
@csrf.exempt
def payment():

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken']
    )

    stripe.Charge.create(
        customer=customer.id,
        amount=4999,
        currency='usd',
        description='Ingite Flask App Code'
    )

    user = User.lookup_or_create_by_email(request.form['stripeEmail'])
    PurchaseReceipt(user).send()

    flash("Payment processed. You'll get an email shortly", 'success')

    return render_template('store/product.html')
