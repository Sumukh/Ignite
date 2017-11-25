from appname.mailers import Mailer, send_email


class ConfirmEmail(Mailer):
    TEMPLATE = 'email/confirm_email.html'
    DEFAULT_SUBJECT = "Confirm your email on appname"

    def send(self):
        user_token = token.generate(
            self.recipient.email, salt='email-confirmation-key')
        link = url_for('auth.confirm', token=user_token, _external=True)
        html_body = render_template(self.TEMPLATE, link=link)
        return self.deliver_later(self.recipient_email, self.subject, html_body)
