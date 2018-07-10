from appname.forms import BaseForm
from wtforms import validators, TextField, PasswordField

from appname.models.user import User

class LoginForm(BaseForm):
    email = TextField('Email', validators=[validators.email(), validators.required()])
    password = PasswordField('Password', validators=[validators.required()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # if our field validators do not pass
        if not check_validate:
            return False

        # Does the user exist?
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
    password = PasswordField('Password', validators=[validators.required(), validators.length(min=4),
                                                     validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', validators=[validators.required()])

    def validate(self):
        check_validate = super(SignupForm, self).validate()

        # if our field validators do not pass
        if not check_validate:
            return False

        # Does the user exist already? Must return false,
        # otherwise we'll allow anyone to sign in
        user = User.lookup(self.email.data)
        if user:
            self.email.errors.append('That email already has an account')
            return False

        return True

class ChangePasswordForm(BaseForm):
    password = PasswordField('Password', validators=[validators.required(),
                                                     validators.length(min=4),
                                                     validators.EqualTo('confirm',
                                                                        message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class RequestPasswordResetForm(BaseForm):
    email = TextField('Email', validators=[validators.email(), validators.required()],
                               description="Enter the email you used")

class SimpleForm(BaseForm):
    pass  # Used for forms that have no input (other than a CSRF check)
