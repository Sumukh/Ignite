import logging
from appname.models import db, Model, transaction
from appname.models.teams import TeamMember

logger = logging.getLogger(__name__)

class Team(Model):
    """
    A team is a collection of users sharing the same resources.
    All users get a team. Some teams have more than one member.
    Most resources in the application should belong to a team.

    Usage:
        team.members -> [<TeamMember>, ...]
    """

    id = db.Column(db.Integer(), primary_key=True)
    creator_id = db.Column(db.ForeignKey("user.id"), index=True,
                           nullable=False)

    name = db.Column(db.String(255))
    # Plan may need to become DB backed when billing is introduced.
    plan = db.Column(db.String(), default='default')

    creator = db.relationship("User")

    @property
    def active_memberships(self):
        return [membership for membership in self.memberships if membership.activated]

    @property
    def active_teams(self):
        return [membership.team for membership in self.memberships if membership.activated]

    @classmethod
    @transaction
    def create(cls, name, creator):
        new_team = cls(name=name, creator=creator)
        new_team_member = TeamMember(team=new_team, user=creator, role='owner', activated=True)

        db.session.add(new_team)
        db.session.add(new_team_member)
        db.session.commit()
        return new_team
