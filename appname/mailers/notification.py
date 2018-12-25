from flask import render_template

from appname.mailers import Mailer

class NotificationMailer(Mailer):
    TEMPLATE = 'email/notification.html'
    DEFAULT_SUBJECT = "[appname] New notification"

    def __init__(self, user, subject, text, link=None, attachments=None):
        self.recipient = None
        self._subject = subject
        self.text = text
        self.recipient_email = user
        self.link = link
        self.attachments = attachments or []

    @property
    def subject(self):
        return self._subject or self.DEFAULT_SUBJECT

    def send(self):
        html_body = render_template(self.TEMPLATE, body=self.text, link=self.link, link_text="View on Appname")
        return self.deliver_now(self.recipient_email, self.subject, html_body,
                                attachments=self.attachments)
