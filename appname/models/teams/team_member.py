import logging

from appname.models import db, Model
from appname.models.user import User
from appname.mailers.teams import InviteEmail

from appname.utils.token import url_safe_token

logger = logging.getLogger(__name__)

class TeamMember(Model):
    id = db.Column(db.Integer(), primary_key=True)
    team_id = db.Column(db.ForeignKey("team.id"), index=True,
                        nullable=False)
    user_id = db.Column(db.ForeignKey("user.id"), index=True,
                        nullable=True)

    invite_email = db.Column(db.String(255))
    role = db.Column(db.String(), default='team_member')

    inviter_id = db.Column(db.ForeignKey("user.id"))
    invite_secret = db.Column(db.String(255), default=url_safe_token)

    activated = db.Column(db.Boolean(), default=False)

    team = db.relationship("Team", backref='members', lazy="joined")
    user = db.relationship("User", foreign_keys=[user_id], backref='memberships')

    inviter = db.relationship("User", foreign_keys=[inviter_id])

    GDPR_EXPORT_COLUMNS = {
        "invite_email": "Email the invite was sent to",
        "activated": "Was the invite activated?",
        "created": "When the invite was created",
        "team_id": "What team was the invite for",
        "inviter_id": "Who sent the invite",
        "role": "Role on team"
    }

    @classmethod
    def invite(cls, team, email, role, inviter):
        invitee = User.lookup(email)
        if (not invitee):
            member = cls(team=team, invite_email=email, role=role, inviter=inviter)
        else:
            member = cls(team=team, user=invitee, role=role, inviter=inviter)

        db.session.add(member)
        db.session.commit()
        InviteEmail(member).send()

    @property
    def email(self):
        if self.user_id:
            return self.user.email
        return self.invite_email

    def activate(self, user_id):
        if not self.activated:
            self.user_id = user_id
            self.activated = True
            db.session.add(self)
            db.session.commit()
            self.team.billing_plan.record_change_in_usage()
        else:
            raise Exception('Already activated')
