from appname.forms import BaseForm
from wtforms import validators, TextField, PasswordField

from appname.models.user import User

class LoginForm(BaseForm):
    email = TextField('Email', validators=[validators.email(), validators.required()])
    password = PasswordField('Password', validators=[validators.optional()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # if our validators do not pass
        if not check_validate:
            return False

        # Does our the exist
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('Invalid email or password')
            return False

        # Do the passwords match
        if not user.check_password(self.password.data):
            self.email.errors.append('Invalid email or password')
            return False

        return True

class SignupForm(BaseForm):
    email = TextField('Email', validators=[validators.email(), validators.required()])
    password = PasswordField('Password', validators=[validators.optional()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # if our validators do not pass
        if not check_validate:
            return False

        # Does our the exist
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('That Email Is Already Registered')
            return False

        return True

# class ChangePasswordForm(BaseForm):
#     password = PasswordField('Password', validators=[validators.required()])

# class ResetPasswordForm(BaseForm):
#     email = TextField('Email', validators=[validators.email(), validators.required()])
