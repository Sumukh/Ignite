from types import SimpleNamespace

import pytest

from appname.controllers import store as store_controller
from appname.controllers.webhooks import stripe as webhook_controller
from appname.models import db
from appname.models.teams import Team
from appname.models.user import User
from appname.utils.token import generate_api_secret

create_user = True


class DummyStripeEvent(dict):
    def __init__(self, event_type, payload_object):
        super().__init__(data={"object": payload_object})
        self.type = event_type


def default_team():
    user = User.lookup("user@example.com")
    assert user is not None
    return user.active_memberships[0].team


@pytest.mark.usefixtures("testapp")
class TestAPI:
    def test_api_info_supports_envelope(self, testapp):
        response = testapp.get("/api/v1/info?envelope=true")

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["code"] == 200
        assert payload["message"] == "success"
        assert payload["data"]["version"] == "v1"

    def test_api_current_user_requires_auth(self, testapp):
        response = testapp.get("/api/v1/user/current")
        assert response.status_code == 401

    def test_api_current_user_accepts_valid_api_key(self, testapp):
        user = User.lookup("user@example.com")
        api_key = generate_api_secret(user)
        user.hash_api_key(api_key)

        response = testapp.get(f"/api/v1/user/current?api_key={api_key}")

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["email"] == "user@example.com"

    def test_api_unknown_route_returns_json_404(self, testapp):
        response = testapp.get("/api/not-a-real-endpoint")

        assert response.status_code == 404
        payload = response.get_json()
        assert payload["code"] == 404


@pytest.mark.usefixtures("testapp")
class TestStore:
    def test_store_home_loads(self, testapp):
        response = testapp.get("/store")
        assert response.status_code == 200

    def test_store_payment_creates_customer_charge_and_user(self, testapp, monkeypatch):
        created = {}

        class CustomerAPI:
            @staticmethod
            def create(email, source):
                created["customer"] = {"email": email, "source": source}
                return SimpleNamespace(id="cus_test_123")

        class ChargeAPI:
            @staticmethod
            def create(**kwargs):
                created["charge"] = kwargs
                return {"id": "ch_test_123"}

        monkeypatch.setattr(store_controller.stripe, "Customer", CustomerAPI)
        monkeypatch.setattr(store_controller.stripe, "Charge", ChargeAPI)
        monkeypatch.setattr(store_controller.PurchaseReceipt, "send", lambda self: True)

        response = testapp.post(
            "/store/payment",
            data={"stripeEmail": "buyer@example.com", "stripeToken": "tok_test_123"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert created["customer"]["email"] == "buyer@example.com"
        assert created["charge"]["customer"] == "cus_test_123"
        assert User.lookup("buyer@example.com") is not None


@pytest.mark.usefixtures("testapp")
class TestStripeWebhooks:
    def test_subscription_deleted_downgrades_team(self, testapp, monkeypatch):
        team = default_team()
        team.subscription_id = "sub_deleted_1"
        team.plan = "monthly_premium"
        db.session.add(team)
        db.session.commit()
        team_id = team.id

        event = DummyStripeEvent("customer.subscription.deleted", {"id": "sub_deleted_1"})
        monkeypatch.setattr(webhook_controller.stripe, "parse_webhook", lambda *_: event)

        response = testapp.post("/webhooks/stripe", data="{}", headers={"Stripe-Signature": "sig"})

        assert response.status_code == 200
        assert db.session.get(Team, team_id).plan == "free"

    def test_subscription_created_sets_plan_and_customer(self, testapp, monkeypatch):
        team = default_team()
        team.subscription_id = "sub_created_1"
        team.plan = "free"
        team.billing_customer_id = None
        db.session.add(team)
        db.session.commit()
        team_id = team.id

        event = DummyStripeEvent(
            "customer.subscription.created",
            {
                "id": "sub_created_1",
                "status": "active",
                "customer": "cus_created_1",
                "plan": {"id": "price_unknown_for_fallback"},
            },
        )
        monkeypatch.setattr(webhook_controller.stripe, "parse_webhook", lambda *_: event)

        response = testapp.post("/webhooks/stripe", data="{}", headers={"Stripe-Signature": "sig"})

        assert response.status_code == 200
        refreshed = db.session.get(Team, team_id)
        assert refreshed.billing_customer_id == "cus_created_1"
        assert refreshed.plan == "monthly_premium"

    def test_subscription_updated_with_cancelled_downgrades_team(self, testapp, monkeypatch):
        team = default_team()
        team.subscription_id = "sub_updated_1"
        team.plan = "annual_premium"
        db.session.add(team)
        db.session.commit()
        team_id = team.id

        event = DummyStripeEvent(
            "customer.subscription.updated",
            {"id": "sub_updated_1", "status": "cancelled"},
        )
        monkeypatch.setattr(webhook_controller.stripe, "parse_webhook", lambda *_: event)

        response = testapp.post("/webhooks/stripe", data="{}", headers={"Stripe-Signature": "sig"})

        assert response.status_code == 200
        assert db.session.get(Team, team_id).plan == "free"

    def test_checkout_completed_sets_subscription_on_team(self, testapp, monkeypatch):
        team = default_team()
        team.subscription_id = None
        team.billing_customer_id = None
        db.session.add(team)
        db.session.commit()
        team_id = team.id

        event = DummyStripeEvent(
            "checkout.session.completed",
            {
                "subscription": "sub_checkout_1",
                "client_reference_id": team_id,
                "customer": "cus_checkout_1",
            },
        )
        monkeypatch.setattr(webhook_controller.stripe, "parse_webhook", lambda *_: event)

        response = testapp.post("/webhooks/stripe", data="{}", headers={"Stripe-Signature": "sig"})

        assert response.status_code == 200
        refreshed = db.session.get(Team, team_id)
        assert refreshed.subscription_id == "sub_checkout_1"
        assert refreshed.billing_customer_id == "cus_checkout_1"

    def test_checkout_completed_with_unknown_team_returns_question_mark(self, testapp, monkeypatch):
        event = DummyStripeEvent(
            "checkout.session.completed",
            {
                "subscription": "sub_checkout_2",
                "client_reference_id": 999999,
                "customer": "cus_checkout_2",
            },
        )
        monkeypatch.setattr(webhook_controller.stripe, "parse_webhook", lambda *_: event)

        response = testapp.post("/webhooks/stripe", data="{}", headers={"Stripe-Signature": "sig"})

        assert response.status_code == 200
        assert response.get_data(as_text=True) == "?"
