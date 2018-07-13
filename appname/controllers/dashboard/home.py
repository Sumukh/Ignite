from flask_login import login_required, current_user

from flask import Blueprint, render_template, flash, redirect, url_for, session, Markup

from appname.constants import REQUIRE_EMAIL_CONFIRMATION
from appname.models import db
from appname.forms.login import ChangePasswordForm
from appname.utils.session import current_membership

blueprint = Blueprint('dashboard_home', __name__)

@blueprint.route('/')
@login_required
def index():
    return render_template('dashboard/home.html')

