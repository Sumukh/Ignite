import pytest

from appname.models import db
from appname.models.user import User
from appname.models.teams.team import Team

create_user = False

@pytest.mark.usefixtures("testapp")
class TestTeam:
    def test_user_creation_of_team(self, testapp):
        """ Test that creating a user, creates a group & a membership """
        user = User('user2@example.com', 'supersafepassword')
        db.session.add(user)
        db.session.commit()

        assert len(user.memberships) == 1
        membership = user.memberships[0]
        assert membership.activated
        assert membership.role == 'administrator'
        assert membership.team.creator == user
