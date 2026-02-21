import pytest

from appname.extensions import hashids
from appname.models.user import User

create_user = True


def login_as_default_user(testapp):
    response = testapp.post(
        "/login",
        data={"email": "user@example.com", "password": "safepassword"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Logged in successfully." in response.get_data(as_text=True)


def default_user_team_hash():
    user = User.lookup("user@example.com")
    assert user is not None
    assert len(user.active_memberships) == 1
    return hashids.encode_id(user.active_memberships[0].team.id)


@pytest.mark.usefixtures("testapp")
class TestSignupAndDashboard:
    def test_signup_page_loads(self, testapp):
        response = testapp.get("/signup")
        assert response.status_code == 200
        assert "Sign up for" in response.get_data(as_text=True)

    def test_signup_creates_user_and_lands_on_dashboard(self, testapp):
        response = testapp.post(
            "/signup",
            data={
                "email": "fresh-user@example.com",
                "password": "supersafepassword",
                "confirm": "supersafepassword",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert "Welcome to appname." in body
        assert "Dashboard" in body

        new_user = User.lookup("fresh-user@example.com")
        assert new_user is not None
        assert new_user.check_password("supersafepassword")
        assert len(new_user.active_memberships) == 1

    def test_signup_rejects_duplicate_email(self, testapp):
        response = testapp.post(
            "/signup",
            data={
                "email": "admin@example.com",
                "password": "supersafepassword",
                "confirm": "supersafepassword",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert "That email already has an account" in response.get_data(as_text=True)

    def test_dashboard_home_loads_for_logged_in_user(self, testapp):
        login_as_default_user(testapp)

        response = testapp.get("/dashboard/", follow_redirects=True)
        assert response.status_code == 200
        assert "Dashboard" in response.get_data(as_text=True)

    def test_dashboard_team_page_loads_for_logged_in_user(self, testapp):
        login_as_default_user(testapp)
        team_hash = default_user_team_hash()

        response = testapp.get(f"/dashboard/{team_hash}/team")
        assert response.status_code == 200
        assert "Invite New Member" in response.get_data(as_text=True)

    def test_dashboard_files_page_loads_for_logged_in_user(self, testapp):
        login_as_default_user(testapp)
        team_hash = default_user_team_hash()

        response = testapp.get(f"/dashboard/{team_hash}/files")
        assert response.status_code == 200
        assert "Add New File" in response.get_data(as_text=True)
