import pytest
from jinja2 import TemplateNotFound

import appname.billing_plans as billing_plans_module
import appname.constants as constants
import appname.controllers.auth as auth_controller
from appname.extensions import hashids, token
from appname.models import db
from appname.models.teams import TeamMember
from appname.models.user import User

create_user = True


class FakeSubscriptionItem(dict):
    def __init__(self, product, item_id):
        super().__init__(product=product)
        self.id = item_id


def login_as_user(testapp, email="user@example.com", password="safepassword"):
    response = testapp.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
    assert response.status_code == 200
    return response


@pytest.mark.usefixtures("testapp")
class TestAuthAdditionalFlows:
    def test_confirm_invalid_token_404(self, testapp):
        response = testapp.get("/confirm/not-a-valid-token")
        assert response.status_code == 404

    def test_confirm_email_logged_out_redirects_login(self, testapp):
        user = User.lookup("user@example.com")
        user.email_confirmed = False
        db.session.add(user)
        db.session.commit()

        code = token.generate(user.email, salt=constants.EMAIL_CONFIRMATION_SALT)
        response = testapp.get(f"/confirm/{code}", follow_redirects=False)

        assert response.status_code == 302
        assert "/login" in response.location
        assert User.lookup("user@example.com").email_confirmed

    def test_confirm_email_logged_in_redirects_dashboard(self, testapp):
        user = User.lookup("user@example.com")
        user.email_confirmed = False
        db.session.add(user)
        db.session.commit()
        login_as_user(testapp)

        code = token.generate(user.email, salt=constants.EMAIL_CONFIRMATION_SALT)
        response = testapp.get(f"/confirm/{code}", follow_redirects=False)

        assert response.status_code == 302
        assert "/dashboard/" in response.location

    def test_resend_confirmation_get_for_unconfirmed_user_raises_for_missing_template(self, testapp):
        user = User.lookup("user@example.com")
        user.email_confirmed = False
        db.session.add(user)
        db.session.commit()
        login_as_user(testapp)

        with pytest.raises(TemplateNotFound):
            testapp.get("/auth/resend-confirmation")

    def test_resend_confirmation_post_sends_email_and_redirects(self, testapp, monkeypatch):
        user = User.lookup("user@example.com")
        user.email_confirmed = False
        db.session.add(user)
        db.session.commit()
        login_as_user(testapp)

        monkeypatch.setattr(auth_controller.ConfirmEmail, "send", lambda self: True)
        response = testapp.post("/auth/resend-confirmation", data={}, follow_redirects=False)

        assert response.status_code == 302
        assert "/dashboard/" in response.location

    def test_request_password_reset_redirects_logged_in_users(self, testapp):
        login_as_user(testapp)
        response = testapp.get("/auth/reset_password", follow_redirects=False)

        assert response.status_code == 302
        assert "/dashboard/" in response.location

    def test_request_password_reset_for_existing_user(self, testapp, monkeypatch):
        monkeypatch.setattr(auth_controller.ResetPassword, "send", lambda self: True)
        response = testapp.post(
            "/auth/reset_password",
            data={"email": "user@example.com"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/login" in response.location

    def test_reset_password_invalid_code_forbidden(self, testapp):
        response = testapp.post(
            "/auth/reset_password/not-valid",
            data={"password": "newpass123", "confirm": "newpass123"},
            follow_redirects=False,
        )
        assert response.status_code == 403

    def test_reset_password_valid_code_updates_user(self, testapp):
        user = User.lookup("user@example.com")
        code = token.generate(user.email, salt=constants.PASSWORD_RESET_SALT)

        response = testapp.post(
            f"/auth/reset_password/{code}",
            data={"password": "newpass123", "confirm": "newpass123"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/dashboard/" in response.location
        assert User.lookup("user@example.com").password == "newpass123"

    def test_reauth_post_with_valid_credentials_redirects_settings(self, testapp):
        response = testapp.post(
            "/reauth",
            data={"email": "user@example.com", "password": "safepassword"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.endswith("/settings")

    def test_join_team_returns_404_for_non_matching_user(self, testapp):
        login_as_user(testapp)
        admin = User.lookup("admin@example.com")
        team = admin.active_memberships[0].team
        invite = TeamMember(team=team, user=admin, role="team member", inviter=admin, activated=False)
        db.session.add(invite)
        db.session.commit()

        response = testapp.get(f"/invite/{hashids.encode_id(invite.id)}/join")
        assert response.status_code == 404

    def test_join_team_activates_invite_for_owner(self, testapp, monkeypatch):
        login_as_user(testapp)
        user = User.lookup("user@example.com")
        team = user.active_memberships[0].team
        invite = TeamMember(team=team, user=user, role="team member", inviter=user, activated=False)
        db.session.add(invite)
        db.session.commit()

        plan = team.billing_plan
        monkeypatch.setattr(
            billing_plans_module.stripe,
            "all_subscription_items",
            lambda _subscription_id: [FakeSubscriptionItem(plan.stripe_product_id, "si_join_1")],
        )
        monkeypatch.setattr(billing_plans_module.stripe, "report_usage", lambda *_args, **_kwargs: None)

        response = testapp.get(f"/invite/{hashids.encode_id(invite.id)}/join", follow_redirects=False)

        assert response.status_code == 302
        assert "/dashboard/" in response.location
        assert TeamMember.query.get(invite.id).activated

    def test_invite_page_renders_for_guest_user(self, testapp):
        user = User.lookup("user@example.com")
        team = user.active_memberships[0].team
        invite = TeamMember(
            team=team,
            invite_email="guest@example.com",
            role="team member",
            inviter=user,
            activated=False,
            invite_secret="secret-123",
        )
        db.session.add(invite)
        db.session.commit()

        response = testapp.get(f"/join/{hashids.encode_id(invite.id)}/secret-123")
        assert response.status_code == 200

    def test_invite_page_rejects_wrong_secret(self, testapp):
        user = User.lookup("user@example.com")
        team = user.active_memberships[0].team
        invite = TeamMember(
            team=team,
            invite_email="guest2@example.com",
            role="team member",
            inviter=user,
            activated=False,
            invite_secret="secret-abc",
        )
        db.session.add(invite)
        db.session.commit()

        response = testapp.get(f"/join/{hashids.encode_id(invite.id)}/wrong-secret")
        assert response.status_code == 404

    def test_invite_page_redirects_owner_to_join(self, testapp):
        login_as_user(testapp)
        user = User.lookup("user@example.com")
        team = user.active_memberships[0].team
        invite = TeamMember(
            team=team,
            user=user,
            role="team member",
            inviter=user,
            activated=False,
            invite_secret="secret-own",
        )
        db.session.add(invite)
        db.session.commit()

        response = testapp.get(f"/join/{hashids.encode_id(invite.id)}/secret-own", follow_redirects=False)
        assert response.status_code == 302
        assert f"/invite/{hashids.encode_id(invite.id)}/join" in response.location
