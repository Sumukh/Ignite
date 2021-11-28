from appname.forms import BaseForm
from wtforms import validators, StringField

class ChangeProfileForm(BaseForm):
    name = StringField('Name', validators=[validators.InputRequired()])
