from appname.forms import BaseForm
from wtforms import validators, TextAreaField, FileField

class FileForm(BaseForm):
    description = TextAreaField('Description')
    attachment = FileField('Attachment', validators=[validators.InputRequired()])
