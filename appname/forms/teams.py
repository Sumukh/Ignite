from appname.forms import BaseForm
from wtforms import validators, TextField, HiddenField, SelectField

from appname.constants import TEAM_MEMBER_ROLES

class InviteMemberForm(BaseForm):
    email = TextField('Email', validators=[validators.email(), validators.required()])
    role = SelectField('Role', default='team member',
                       choices=[(r, r.title()) for r in TEAM_MEMBER_ROLES])



