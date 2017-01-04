from flask import redirect, url_for, request
from flask_login import current_user

import flask_admin as admin
from flask_admin.form import SecureForm
from flask_admin.contrib import sqla

from appname.models import db
from appname.models.user import User

class AdminHomeView(admin.AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

class AdminModelView(sqla.ModelView):
    form_base_class = SecureForm
    form_excluded_columns = ['password', 'created']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

class UserView(AdminModelView):
    column_searchable_list = ['email']
    column_list = ['id', 'admin', 'email', 'created']
    column_exclude_list = ['password']
    column_filters = ['admin']
    can_export = True

class AdminDashboard:
    def __init__(self):
        self.dashboard = admin.Admin(name='appname', template_mode='bootstrap3',
                                     index_view=AdminHomeView())
        self.dashboard.add_view(UserView(User, db.session))

    def init_app(self, app):
        self.dashboard.init_app(app)
        return self.dashboard
