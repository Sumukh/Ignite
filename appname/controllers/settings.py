from flask import Blueprint, render_template
from flask_login import login_required, current_user

from appname.extensions import cache

settings_blueprint = Blueprint('settings', __name__)

@settings_blueprint.route('/settings')
@login_required
def settings():
    return render_template('settings/index.html')
