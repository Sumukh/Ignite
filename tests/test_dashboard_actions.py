import io

import pytest

from appname.extensions import hashids, storage
from appname.models import db
from appname.models.team_file import TeamFile
from appname.models.teams import TeamMember
from appname.models.user import User

create_user = True


def login_as_user(testapp, email="user@example.com", password="safepassword"):
    response = testapp.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Logged in successfully." in response.get_data(as_text=True)


def user_team_and_hash(email="user@example.com"):
    user = User.lookup(email)
    assert user is not None
    team = user.active_memberships[0].team
    return user, team, hashids.encode_id(team.id)


class DummyUpload:
    def __init__(self, name="document.txt", object_name="uploaded-1"):
        self.info = {"name": name}
        self.name = object_name
        self.url = "https://example.com/files/document.txt"


@pytest.mark.usefixtures("testapp")
class TestDashboardActions:
    def test_add_member_creates_invite(self, testapp):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()

        response = testapp.post(
            f"/dashboard/{team_hash}/team/add_member",
            data={"email": "invitee@example.com", "role": "team member"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        invite = TeamMember.query.filter_by(team=team, invite_email="invitee@example.com").first()
        assert invite is not None
        assert invite.inviter == user

    def test_add_member_skips_existing_member(self, testapp):
        login_as_user(testapp)
        _, team, team_hash = user_team_and_hash()
        count_before = TeamMember.query.filter_by(team=team).count()

        response = testapp.post(
            f"/dashboard/{team_hash}/team/add_member",
            data={"email": "user@example.com", "role": "team member"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        count_after = TeamMember.query.filter_by(team=team).count()
        assert count_after == count_before

    def test_remove_pending_member_deletes_membership(self, testapp):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        pending = TeamMember(team=team, invite_email="remove-me@example.com", role="team member", inviter=user)
        db.session.add(pending)
        db.session.commit()
        invite_hash = hashids.encode_id(pending.id)

        response = testapp.post(
            f"/dashboard/{team_hash}/team/{invite_hash}/remove_member",
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert TeamMember.query.get(pending.id) is None

    def test_remove_last_active_user_is_blocked(self, testapp):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        self_membership_hash = hashids.encode_id(user.active_memberships[0].id)

        response = testapp.post(
            f"/dashboard/{team_hash}/team/{self_membership_hash}/remove_member",
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert TeamMember.query.get(user.active_memberships[0].id) is not None

    def test_add_file_creates_team_file_record(self, testapp, monkeypatch):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        user_id = user.id

        monkeypatch.setattr(storage, "upload", lambda _: DummyUpload(name="report.txt", object_name="file-1"))

        response = testapp.post(
            f"/dashboard/{team_hash}/files/add_file",
            data={
                "description": "Quarterly report",
                "attachment": (io.BytesIO(b"content"), "report.txt"),
            },
            content_type="multipart/form-data",
            follow_redirects=False,
        )

        assert response.status_code == 302
        saved = TeamFile.query.filter_by(team=team, file_name="report.txt").first()
        assert saved is not None
        assert saved.user_id == user_id
        assert saved.description == "Quarterly report"

    def test_download_file_redirects_to_storage_url(self, testapp, monkeypatch):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        team_file = TeamFile(team=team, user=user, file_name="doc.txt", file_object_name="obj-2")
        db.session.add(team_file)
        db.session.commit()

        class StoredObject:
            def download_url(self):
                return "https://example.com/download/doc.txt"

        monkeypatch.setattr(storage, "get", lambda _: StoredObject())

        response = testapp.get(f"/dashboard/{team_hash}/files/{hashids.encode_id(team_file.id)}")

        assert response.status_code == 302
        assert response.location.endswith("/download/doc.txt")

    def test_destroy_file_removes_file_and_storage_object(self, testapp, monkeypatch):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        team_file = TeamFile(team=team, user=user, file_name="old.txt", file_object_name="obj-3")
        db.session.add(team_file)
        db.session.commit()

        class StoredObject:
            def __init__(self):
                self.deleted = False

            def delete(self):
                self.deleted = True

        stored = StoredObject()
        monkeypatch.setattr(storage, "get", lambda _: stored)

        response = testapp.post(
            f"/dashboard/{team_hash}/files/{hashids.encode_id(team_file.id)}/destroy",
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert TeamFile.query.get(team_file.id) is None
        assert stored.deleted
