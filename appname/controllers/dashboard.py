from flask_login import login_required, current_user

from flask import Blueprint, render_template
from appname.extensions import cache

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
@login_required
def home():
    return render_template('dashboard/home.html')

@dashboard.route('/dashboard/settings')
@login_required
def settings():
    return render_template('dashboard/settings.html')

