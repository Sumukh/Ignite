from appname.forms import BaseForm
from wtforms import validators, StringField, SelectField

from appname.constants import TEAM_MEMBER_ROLES

class InviteMemberForm(BaseForm):
    email = StringField('Email', validators=[validators.email(), validators.InputRequired()])
    role = SelectField('Role', default='team member',
                       choices=[(r, r.title()) for r in TEAM_MEMBER_ROLES])
