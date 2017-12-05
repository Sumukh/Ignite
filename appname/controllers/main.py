from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

from appname.extensions import cache

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return render_template('index.html')

@main.route('/beta')
@cache.cached(timeout=1000, unless=lambda: current_user.is_authenticated)
def beta():
    return "Coming Soon", 200
