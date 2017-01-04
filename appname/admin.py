from flask import redirect, url_for, request, abort
from flask_login import current_user
import flask_admin as admin
from flask_admin.contrib import sqla

from appname.models import db
from appname.models.user import User

class AdminHomeView(admin.AdminIndexView):
    @admin.expose('/')
    def index(self):
        abort(404)

class AdminModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

class AdminDashboard:
    def __init__(self):
        self.dashboard = admin.Admin(name='appname', template_mode='bootstrap3', index_view=AdminHomeView())
        self.dashboard.add_view(AdminModelView(User, db.session))

    def init_app(self, app):
        self.dashboard.init_app(app)
        return self.dashboard
