from flask import Blueprint, render_template
from flask_login import login_required

from appname.extensions import cache

main = Blueprint('main', __name__)

@main.route('/')
@cache.cached(timeout=1000)
def home():
    return render_template('index.html')

@main.route("/restricted")
@login_required
def restricted():
    return "You can only see this if you are logged in!", 200
