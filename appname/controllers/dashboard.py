from flask_login import login_required, current_user

from flask import Blueprint, render_template, flash, redirect, url_for, Markup

from appname.models import db
dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard')
@login_required
def home():
    return render_template('dashboard/home.html')

