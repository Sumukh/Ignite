from flask import render_template, url_for

from appname.mailers import Mailer

class InviteEmail(Mailer):
    TEMPLATE = 'email/teams/invite.html'

    def __init__(self, invite):
        self.recipient = None
        self.invite = invite
        self.recipient_email = invite.invite_email or (invite.user and invite.user.email)

    @property
    def subject(self):
        return ("{0} invited you to join their team on appname"
                .format(self.invite.inviter.email))

    def send(self):
        link = url_for('auth.invite_page', invite_id=self.invite.id,
                       secret=self.invite.invite_secret, _external=True)
        html_body = render_template(self.TEMPLATE, link=link, invite=self.invite)
        return self.deliver_now(self.recipient_email, self.subject, html_body)
