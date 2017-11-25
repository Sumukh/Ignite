# A simple way to send emails using Flask-Mail
# Documentation: http://pythonhosted.org/Flask-Mail/

import collections

from flask import render_template, url_for
from flask_mail import Message

from appname.extensions import mail, rq2

@rq2.job 
def send_email(to_emails, subject, html_body,
               text_body=None, conn=None, **kwargs):
    """ Send emails.
    Params: 
    * `conn`: Use to send multiple messages in the same connection
             (https://pythonhosted.org/Flask-Mail#bulk-emails)

    Usage: 
    send_email('user@example.com', 'Hey from appname', 'this is the message',
                cc=['test@example.com'], reply_to='appname@example.com')
    send_email(['user@example.com'], 'Hey from appname', 'this is the message',
                reply_to='appname@example.com')
    """
    if not isinstance(to_emails, list):
        to_emails = [to_emails]
    conn = conn or mail
    message = Message(subject, recipients=to_emails, **kwargs)

    message.body = text_body or html_body
    message.html = html_body

    return conn.send(message)

class Mailer:
    TEMPLATE = 'email/notification.html'
    DEFAULT_SUBJECT = "New Message from appname"
    DEFAULT_LINK_TEXT = None 
    DEFAULT_LINK_URL = None 

    def __init__(self, recipient):
        self.recipient = recipient
        self.recipient_email = recipient.email

    @property
    def subject(self):
        return DEFAULT_SUBJECT 

    def deliver_later(to_emails, subject, html_body, **kwargs):
        # Wrapper method to queue up the original send_email_raw
        return send_email_raw.queue(to_emails, subject, html_body, **kwargs)

    def deliver_now(to_emails, subject, html_body, **kwargs):
        # Wrapper method to call the original send_email_raw
        return send_email_raw(to_emails, subject, html_body, **kwargs)

    def send(self, body):
        html_body = render_template(self.TEMPLATE, body=body)
        return self.deliver_later(self.recipient_email, self.subject, html_body, text_body=text)

        
