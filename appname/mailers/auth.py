from flask import render_template, url_for

from appname.constants import EMAIL_CONFIRMATION_SALT
from appname.mailers import Mailer
from appname.extensions import token

class ConfirmEmail(Mailer):
    TEMPLATE = 'email/confirm_email.html'
    DEFAULT_SUBJECT = "Confirm your email on appname"

    def send(self):
        if self.recipient.email_confirmed:
            return False
        user_token = token.generate(
            self.recipient.email, salt=EMAIL_CONFIRMATION_SALT)
        link = url_for('auth.confirm', code=user_token, _external=True)
        html_body = render_template(self.TEMPLATE, link=link)
        return self.deliver_later(self.recipient_email, self.subject, html_body)
