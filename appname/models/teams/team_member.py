import logging

from sqlalchemy.orm import backref

from appname.models import db, Model, ModelProxy
from appname.models.user import User

from appname.utils.token import url_safe_token

logger = logging.getLogger(__name__)

class TeamMember(Model):
    id = db.Column(db.Integer(), primary_key=True)
    team_id = db.Column(db.ForeignKey("team.id"), index=True,
                        nullable=False)
    user_id = db.Column(db.ForeignKey("user.id"), index=True,
                        nullable=True)

    invite_email = db.Column(db.String(255))
    role = db.Column(db.String(), default='member')

    inviter_id = db.Column(db.ForeignKey("user.id"))
    invite_secret = db.Column(db.String(255), default=url_safe_token)

    activated = db.Column(db.Boolean(), default=False)

    team = db.relationship("Team", backref='members', lazy="joined")
    user = db.relationship("User", foreign_keys=[user_id], backref='memberships')

    inviter = db.relationship("User", foreign_keys=[inviter_id])

    @classmethod
    def invite(cls, team, email, role, inviter):
        invitee = User.lookup(email)
        if (not invitee):
            member = ModelProxy.teams.TeamMember(team=team, invite_email=email, role=role, inviter=inviter)
        else:
            member = ModelProxy.teams.TeamMember(team=team, user=invitee, role=role, inviter=inviter)

        db.session.add(member)
        db.session.commit()