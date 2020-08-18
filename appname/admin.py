from flask import redirect, url_for, request
from flask_login import current_user

import flask_admin as admin
from flask_admin.form import SecureForm
from flask_admin.contrib import sqla

from appname.models import db, ModelProxy
from appname.models.user import User

# Unfortunately, ModelProxy seems to be the only way to safely import other models
# because `AdminDashboard` itself is used in `extensions.py`. There's probably a
# workaround, but all of the ones I see now are also not great
# (ex: importing in the `init_app` method instead of the top of the file)

class AdminHomeView(admin.AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

    @admin.expose('/')
    def index(self):
        team_model = ModelProxy.teams.Team
        self._template_args['user_count'] = User.query.count()
        self._template_args['team_count'] = team_model.query.count()
        self._template_args['paid_count'] = team_model.query.filter(team_model.plan != 'free').count()
        return super(AdminHomeView, self).index()


class AdminModelView(sqla.ModelView):
    form_base_class = SecureForm
    form_excluded_columns = ['password', 'created']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

class UserView(AdminModelView):
    column_searchable_list = ['email']
    column_list = ['id', 'admin', 'email', 'created']
    column_exclude_list = ['password']
    column_filters = ['admin']
    can_export = True

class TeamView(AdminModelView):
    column_searchable_list = ['name']
    column_list = ['id', 'plan', 'creator', 'subscription_id', 'created']
    column_exclude_list = []
    column_filters = ['plan']
    can_export = True

class TeamMemberView(AdminModelView):
    column_searchable_list = ['invite_email']
    column_list = ['id', 'team', 'role', 'user', 'inviter', 'invite_email', 'activated']
    column_exclude_list = []
    column_filters = ['activated']
    can_export = True

class AdminDashboard:
    def init_app(self, app):
        self.dashboard = admin.Admin(name='appname', template_mode='bootstrap3',
                                     index_view=AdminHomeView(template='admin/index.html'))

        self.dashboard.add_view(UserView(User, db.session))
        # self.dashboard.add_view(TeamView(ModelProxy.teams.Team, db.session))
        # self.dashboard.add_view(TeamMemberView(ModelProxy.teams.TeamMember, db.session))

        self.dashboard.init_app(app)
        return self.dashboard
