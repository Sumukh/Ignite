from appname.forms import BaseForm
from wtforms import validators, TextField

class ChangeProfileForm(BaseForm):
    name = TextField('Name', validators=[validators.required()])
