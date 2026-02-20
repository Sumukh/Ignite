from types import SimpleNamespace

import appname.helpers.session as session_helper
import pytest

create_user = True


def login_as_user(testapp, email="user@example.com", password="safepassword"):
    response = testapp.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return response


@pytest.mark.usefixtures("testapp")
class TestAdminJobsAuth:
    def test_jobs_dashboard_requires_authentication(self, testapp):
        response = testapp.get("/admin/rq/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_jobs_dashboard_for_non_admin_returns_403(self, testapp):
        login_as_user(testapp)
        response = testapp.get("/admin/rq/", follow_redirects=False)
        assert response.status_code == 403


@pytest.mark.usefixtures("testapp")
class TestSessionHelper:
    def test_current_membership_defaults_to_first_active_membership(self, testapp, monkeypatch):
        membership_1 = SimpleNamespace(id=1)
        membership_2 = SimpleNamespace(id=2)
        monkeypatch.setattr(
            session_helper,
            "current_user",
            SimpleNamespace(active_memberships=[membership_1, membership_2]),
        )

        with testapp.application.test_request_context("/"):
            assert session_helper.current_membership() == membership_1

    def test_current_membership_returns_selected_membership(self, testapp, monkeypatch):
        membership_1 = SimpleNamespace(id=1)
        membership_2 = SimpleNamespace(id=2)
        monkeypatch.setattr(
            session_helper,
            "current_user",
            SimpleNamespace(active_memberships=[membership_1, membership_2]),
        )

        with testapp.application.test_request_context("/"):
            from flask import session

            session["current_team_membership_id"] = 2
            assert session_helper.current_membership() == membership_2

    def test_current_membership_redirects_when_session_membership_is_invalid(self, testapp, monkeypatch):
        membership_1 = SimpleNamespace(id=1)
        monkeypatch.setattr(
            session_helper,
            "current_user",
            SimpleNamespace(active_memberships=[membership_1]),
        )

        with testapp.application.test_request_context("/"):
            from flask import session

            session["current_team_membership_id"] = 99
            response = session_helper.current_membership()

        assert response.status_code == 302
        assert response.location.endswith("/")

