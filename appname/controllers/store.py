import stripe

from flask_login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for, request

from appname.models.user import User
from appname.mailers.store import PurchaseReceipt

store = Blueprint('store', __name__)

@store.route('/store')
def home():
    return render_template('store/product.html', stripe_publishable_key=stripe.publishable_key)


@store.route('/store/payment', methods=['POST'])
def payment():

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=4999,
        currency='usd',
        description='Ingite Flask App Code'
    )

    user = User.lookup_or_create(request.form['stripeEmail'])
    PurchaseReceipt(user).send()

    flash("Payment processed. You'll get an email shortly", 'success')

    return render_template('store/product.html')
