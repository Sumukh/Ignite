from flask import render_template, url_for

import appname.constants as constants
from appname.mailers import Mailer
from appname.extensions import token

class ConfirmEmail(Mailer):
    TEMPLATE = 'email/confirm_email.html'
    DEFAULT_SUBJECT = "Confirm your email on appname"

    def send(self):
        if self.recipient.email_confirmed:
            return False
        user_token = token.generate(
            self.recipient.email, salt=constants.EMAIL_CONFIRMATION_SALT)
        link = url_for('auth.confirm', code=user_token, _external=True)
        html_body = render_template(self.TEMPLATE, link=link)
        return self.deliver_later(self.recipient_email, self.subject, html_body)

class ResetPassword(Mailer):
    TEMPLATE = 'email/reset_password.html'
    DEFAULT_SUBJECT = "appname Password Reset"

    def send(self):
        user_token = token.generate(
            self.recipient.email, salt=constants.PASSWORD_RESET_SALT)
        link = url_for('auth.reset_password', code=user_token, _external=True)
        html_body = render_template(self.TEMPLATE, link=link)
        return self.deliver_later(self.recipient_email, self.subject, html_body)
