import io

import pytest

import appname.controllers.dashboard.files as files_controller
import appname.controllers.dashboard.team as team_controller
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
    def test_dashboard_home_redirects_to_memberships_when_user_has_no_active_team(self, testapp):
        login_as_user(testapp)
        user = User.lookup("user@example.com")

        for membership in user.memberships:
            membership.activated = False
            db.session.add(membership)
        db.session.commit()

        response = testapp.get("/dashboard/", follow_redirects=False)
        assert response.status_code == 302
        assert "/settings/memberships" in response.location

    def test_dashboard_home_404_for_team_non_member(self, testapp):
        login_as_user(testapp)
        admin = User.lookup("admin@example.com")
        other_team_hash = hashids.encode_id(admin.active_memberships[0].team.id)

        response = testapp.get(f"/dashboard/{other_team_hash}")
        assert response.status_code == 404

    def test_team_dashboard_redirects_home_when_user_has_no_primary_membership(self, testapp):
        login_as_user(testapp)
        user, _, team_hash = user_team_and_hash()

        for membership in user.memberships:
            membership.activated = False
            db.session.add(membership)
        db.session.commit()

        response = testapp.get(f"/dashboard/{team_hash}/team", follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith("/")

    def test_team_dashboard_404_for_team_non_member(self, testapp):
        login_as_user(testapp)
        admin = User.lookup("admin@example.com")
        other_team_hash = hashids.encode_id(admin.active_memberships[0].team.id)

        response = testapp.get(f"/dashboard/{other_team_hash}/team")
        assert response.status_code == 404

    def test_add_member_404_for_invalid_team(self, testapp):
        login_as_user(testapp)
        invalid_team_hash = hashids.encode_id(999999)

        response = testapp.post(
            f"/dashboard/{invalid_team_hash}/team/add_member",
            data={"email": "missing@example.com", "role": "team member"},
            follow_redirects=False,
        )

        assert response.status_code == 404

    def test_add_member_blocks_when_plan_limit_reached(self, testapp):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()

        for idx in range(4):
            db.session.add(
                TeamMember(
                    team=team,
                    invite_email=f"full-{idx}@example.com",
                    role="team member",
                    inviter=user,
                )
            )
        db.session.commit()

        before_count = TeamMember.query.filter_by(team=team).count()
        response = testapp.post(
            f"/dashboard/{team_hash}/team/add_member",
            data={"email": "new-after-limit@example.com", "role": "team member"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        after_count = TeamMember.query.filter_by(team=team).count()
        assert after_count == before_count

    def test_add_member_invalid_form_redirects(self, testapp, monkeypatch):
        login_as_user(testapp)
        _, _, team_hash = user_team_and_hash()
        monkeypatch.setattr(team_controller.InviteMemberForm, "validate_on_submit", lambda _self: False)

        response = testapp.post(
            f"/dashboard/{team_hash}/team/add_member",
            data={"email": "bad-email"},
            follow_redirects=False,
        )
        assert response.status_code == 302

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

    def test_billing_portal_redirects_to_customer_portal(self, testapp, monkeypatch):
        login_as_user(testapp)
        _, team, team_hash = user_team_and_hash()
        team.billing_customer_id = "cus_123"
        db.session.add(team)
        db.session.commit()

        monkeypatch.setattr(team_controller.stripe, "customer_portal_link", lambda _customer_id: "https://billing.example.com")

        response = testapp.post(
            f"/dashboard/{team_hash}/team/billing_portal",
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == "https://billing.example.com"

    def test_billing_portal_falls_back_to_settings_without_customer(self, testapp):
        login_as_user(testapp)
        _, team, team_hash = user_team_and_hash()
        team.billing_customer_id = None
        db.session.add(team)
        db.session.commit()

        response = testapp.post(
            f"/dashboard/{team_hash}/team/billing_portal",
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/settings/billing" in response.location

    def test_billing_portal_404_for_invalid_team(self, testapp):
        login_as_user(testapp)
        invalid_team_hash = hashids.encode_id(999999)

        response = testapp.post(
            f"/dashboard/{invalid_team_hash}/team/billing_portal",
            data={},
            follow_redirects=False,
        )
        assert response.status_code == 404

    def test_remove_member_404_when_membership_not_found(self, testapp):
        login_as_user(testapp)
        _, _, team_hash = user_team_and_hash()
        missing_invite_hash = hashids.encode_id(999999)

        response = testapp.post(
            f"/dashboard/{team_hash}/team/{missing_invite_hash}/remove_member",
            data={},
            follow_redirects=False,
        )
        assert response.status_code == 404

    def test_remove_creator_is_blocked(self, testapp):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()

        extra_user = User("second-member@example.com", "safepassword2")
        db.session.add(extra_user)
        db.session.commit()
        db.session.add(
            TeamMember(
                team=team,
                user=extra_user,
                role="team member",
                inviter=user,
                activated=True,
            )
        )
        db.session.commit()

        creator_membership_id = user.active_memberships[0].id
        creator_membership_hash = hashids.encode_id(creator_membership_id)
        response = testapp.post(
            f"/dashboard/{team_hash}/team/{creator_membership_hash}/remove_member",
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert db.session.get(TeamMember, creator_membership_id) is not None

    def test_remove_member_invalid_form_redirects(self, testapp, monkeypatch):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        pending = TeamMember(team=team, invite_email="no-remove@example.com", role="team member", inviter=user)
        db.session.add(pending)
        db.session.commit()

        monkeypatch.setattr(team_controller.SimpleForm, "validate_on_submit", lambda _self: False)

        response = testapp.post(
            f"/dashboard/{team_hash}/team/{hashids.encode_id(pending.id)}/remove_member",
            data={},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert db.session.get(TeamMember, pending.id) is not None

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
        assert db.session.get(TeamMember, pending.id) is None

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
        assert db.session.get(TeamMember, user.active_memberships[0].id) is not None

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

    def test_files_dashboard_redirects_home_when_user_has_no_primary_membership(self, testapp):
        login_as_user(testapp)
        user, _, team_hash = user_team_and_hash()
        for membership in user.memberships:
            membership.activated = False
            db.session.add(membership)
        db.session.commit()

        response = testapp.get(f"/dashboard/{team_hash}/files", follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith("/")

    def test_files_dashboard_404_for_team_non_member(self, testapp):
        login_as_user(testapp)
        admin = User.lookup("admin@example.com")
        other_team_hash = hashids.encode_id(admin.active_memberships[0].team.id)

        response = testapp.get(f"/dashboard/{other_team_hash}/files")
        assert response.status_code == 404

    def test_add_file_404_for_invalid_team(self, testapp):
        login_as_user(testapp)
        invalid_team_hash = hashids.encode_id(999999)

        response = testapp.post(
            f"/dashboard/{invalid_team_hash}/files/add_file",
            data={},
            follow_redirects=False,
        )
        assert response.status_code == 404

    def test_add_file_invalid_form_raises_type_error(self, testapp, monkeypatch):
        login_as_user(testapp)
        _, _, team_hash = user_team_and_hash()
        monkeypatch.setattr(files_controller.FileForm, "validate_on_submit", lambda _self: False)

        with pytest.raises(TypeError):
            testapp.post(
                f"/dashboard/{team_hash}/files/add_file",
                data={},
                follow_redirects=False,
            )

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

    def test_download_file_404_when_storage_returns_none(self, testapp, monkeypatch):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        team_file = TeamFile(team=team, user=user, file_name="missing.txt", file_object_name="obj-404")
        db.session.add(team_file)
        db.session.commit()

        monkeypatch.setattr(storage, "get", lambda _: None)
        response = testapp.get(f"/dashboard/{team_hash}/files/{hashids.encode_id(team_file.id)}")
        assert response.status_code == 404

    def test_destroy_file_404_for_invalid_team(self, testapp):
        login_as_user(testapp)
        invalid_team_hash = hashids.encode_id(999999)

        response = testapp.post(
            f"/dashboard/{invalid_team_hash}/files/{hashids.encode_id(1)}/destroy",
            data={},
            follow_redirects=False,
        )
        assert response.status_code == 404

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
        assert db.session.get(TeamFile, team_file.id) is None
        assert stored.deleted

    def test_destroy_file_removes_db_record_when_storage_object_missing(self, testapp, monkeypatch):
        login_as_user(testapp)
        user, team, team_hash = user_team_and_hash()
        team_file = TeamFile(team=team, user=user, file_name="nostorage.txt", file_object_name="obj-no-storage")
        db.session.add(team_file)
        db.session.commit()

        monkeypatch.setattr(storage, "get", lambda _: None)
        response = testapp.post(
            f"/dashboard/{team_hash}/files/{hashids.encode_id(team_file.id)}/destroy",
            data={},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert db.session.get(TeamFile, team_file.id) is None
