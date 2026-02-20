import datetime as dt
import json
from types import SimpleNamespace

import pytest
import pytz

import appname.billing_plans as billing_plans_module
import appname.helpers.gdpr as gdpr_module
import appname.services.stripe as stripe_service_module
from appname.billing_plans import FreePlan, MeteredPlan, MonthlyPremium
from appname.helpers.gdpr import GDPRExport
from appname.mailers.notification import NotificationMailer
from appname.models.user import User
from appname.services.stripe import Stripe
from appname.utils import math as math_utils
from appname.utils import text as text_utils
from appname.utils import time as time_utils
from appname.utils import token as token_utils

create_user = True


class FakeSubscriptionItem(dict):
    def __init__(self, product, item_id):
        super().__init__(product=product)
        self.id = item_id


@pytest.mark.usefixtures("testapp")
class TestGDPRExport:
    def test_export_user_pii_json_includes_user_and_related_models(self, testapp):
        user = User.lookup("user@example.com")
        payload = json.loads(GDPRExport(user, user).export_user_pii_json())

        assert "User" in payload
        assert "Team" in payload
        assert "TeamMember" in payload

    def test_export_denies_non_admin_requesting_other_user(self, testapp):
        user = User.lookup("user@example.com")
        admin = User.lookup("admin@example.com")

        with pytest.raises(Exception):
            GDPRExport(admin, user)

    def test_send_pii_export_builds_mail_with_attachment(self, testapp, monkeypatch):
        user = User.lookup("user@example.com")
        sent = {}

        class FakeMailer:
            def __init__(self, recipient_email, subject, body, attachments=None):
                sent["recipient_email"] = recipient_email
                sent["subject"] = subject
                sent["body"] = body
                sent["attachments"] = attachments or []

            def send(self):
                sent["sent"] = True

        monkeypatch.setattr(gdpr_module, "NotificationMailer", FakeMailer)
        GDPRExport(user, user).send_pii_export()

        assert sent["sent"]
        assert sent["recipient_email"] == "user@example.com"
        assert len(sent["attachments"]) == 1


@pytest.mark.usefixtures("testapp")
class TestStripeService:
    def test_create_customer_returns_existing_customer_id(self, testapp, monkeypatch):
        user = User.lookup("user@example.com")
        user.billing_customer_id = "cus_existing"

        called = {"count": 0}

        def fail_create(*_args, **_kwargs):
            called["count"] += 1
            raise AssertionError("Customer.create should not be called")

        monkeypatch.setattr(stripe_service_module.stripe.Customer, "create", fail_create)

        stripe_service = Stripe()
        assert stripe_service.create_customer(user) == "cus_existing"
        assert called["count"] == 0

    def test_create_customer_creates_and_persists_id(self, testapp, monkeypatch):
        user = User.lookup("user@example.com")
        user.billing_customer_id = None

        monkeypatch.setattr(
            stripe_service_module.stripe.Customer,
            "create",
            lambda **_kwargs: SimpleNamespace(id="cus_new_123"),
        )

        stripe_service = Stripe()
        result = stripe_service.create_customer(user)

        assert result == "cus_new_123"
        assert user.billing_customer_id == "cus_new_123"

    def test_customer_portal_link(self, testapp, monkeypatch):
        stripe_service = Stripe()

        no_customer_owner = SimpleNamespace(billing_customer_id=None)
        assert stripe_service.customer_portal_link(no_customer_owner, return_url="https://example.com/return") is None

        monkeypatch.setattr(
            stripe_service_module.stripe.billing_portal.Session,
            "create",
            lambda **_kwargs: {"url": "https://example.com/portal"},
        )
        owner = SimpleNamespace(billing_customer_id="cus_portal_1")
        link = stripe_service.customer_portal_link(owner, return_url="https://example.com/return")
        assert link == "https://example.com/portal"

    def test_usage_reporting_and_subscription_item_listing(self, testapp, monkeypatch):
        calls = {}

        def fake_create_usage_record(subscription_item_id, quantity, timestamp, action):
            calls["usage"] = {
                "subscription_item_id": subscription_item_id,
                "quantity": quantity,
                "action": action,
                "timestamp": timestamp,
            }

        monkeypatch.setattr(
            stripe_service_module.stripe.SubscriptionItem,
            "create_usage_record",
            fake_create_usage_record,
        )
        monkeypatch.setattr(
            stripe_service_module.stripe.SubscriptionItem,
            "list",
            lambda **_kwargs: {"data": [{"id": "si_1"}]},
        )

        stripe_service = Stripe()
        stripe_service.report_usage("si_1", 7, action="set")
        items = stripe_service.all_subscription_items("sub_1")

        assert calls["usage"]["subscription_item_id"] == "si_1"
        assert calls["usage"]["quantity"] == 7
        assert calls["usage"]["action"] == "set"
        assert items == [{"id": "si_1"}]

    def test_parse_webhook_uses_signature_header(self, testapp, monkeypatch):
        captured = {}

        def fake_construct_event(payload, signature, webhook_key):
            captured["payload"] = payload
            captured["signature"] = signature
            captured["webhook_key"] = webhook_key
            return {"ok": True}

        monkeypatch.setattr(stripe_service_module.stripe.Webhook, "construct_event", fake_construct_event)

        stripe_service = Stripe()
        stripe_service.webhook_key = "whsec_test"
        event = stripe_service.parse_webhook("{}", {"Stripe-Signature": "sig_123"})

        assert event == {"ok": True}
        assert captured["signature"] == "sig_123"
        assert captured["webhook_key"] == "whsec_test"


@pytest.mark.usefixtures("testapp")
class TestBillingPlans:
    def test_free_plan_member_limit(self, testapp):
        small_team = SimpleNamespace(members=[1, 2, 3, 4])
        large_team = SimpleNamespace(members=[1, 2, 3, 4, 5])

        assert FreePlan(small_team).can_add_more_users
        assert not FreePlan(large_team).can_add_more_users

    def test_metered_plan_records_usage(self, testapp, monkeypatch):
        team = SimpleNamespace(id=10, subscription_id="sub_metered_1", active_members=[1, 2, 3], members=[])
        plan = MeteredPlan(team)
        calls = {}

        monkeypatch.setattr(
            billing_plans_module.stripe,
            "all_subscription_items",
            lambda _subscription_id: [FakeSubscriptionItem(plan.stripe_product_id, "si_metered_1")],
        )
        monkeypatch.setattr(
            billing_plans_module.stripe,
            "report_usage",
            lambda subscription_item_id, quantity: calls.update(
                {"subscription_item_id": subscription_item_id, "quantity": quantity}
            ),
        )

        plan.record_change_in_usage()
        assert calls["subscription_item_id"] == "si_metered_1"
        assert calls["quantity"] == 3

    def test_metered_plan_raises_when_subscription_item_missing(self, testapp, monkeypatch):
        team = SimpleNamespace(id=11, subscription_id="sub_metered_2", active_members=[1], members=[])
        plan = MeteredPlan(team)

        monkeypatch.setattr(billing_plans_module.stripe, "all_subscription_items", lambda _subscription_id: [])

        with pytest.raises(Exception):
            plan.record_change_in_usage()

    def test_set_team_plan_updates_team_value(self, testapp):
        user = User.lookup("user@example.com")
        team = user.active_memberships[0].team
        team.plan = "free"

        MonthlyPremium(team).set_team_plan()
        assert team.plan == "monthly_premium"


@pytest.mark.usefixtures("testapp")
class TestUtilsAndMailers:
    def test_math_helpers(self, testapp):
        assert math_utils.ceildiv(9, 2) == 5
        chunks = list(math_utils.chunks(list(range(10)), 3))
        assert [len(chunk) for chunk in chunks] == [4, 3, 3]

    def test_text_pluralize(self, testapp):
        assert text_utils.pluralize(1) == ""
        assert text_utils.pluralize(2) == "s"
        assert text_utils.pluralize(2, singular=" item", plural=" items") == " items"

    def test_time_helpers(self, testapp):
        pacific = pytz.timezone("US/Pacific")
        naive = dt.datetime(2020, 1, 1, 12, 0, 0)

        local_obj = time_utils.local_time_obj(naive, pacific)
        assert local_obj.tzinfo is not None

        server_obj = time_utils.server_time_obj(naive, pacific)
        assert server_obj.tzinfo == pytz.utc

        future = time_utils.future_time_obj(pacific, days=1)
        assert future.hour == 23
        assert future.minute == 59
        assert future.second == 59

    def test_token_helpers(self, testapp):
        token = token_utils.url_safe_token()
        assert len(token) == 9
        assert "-" not in token
        assert "_" not in token
        assert "=" not in token

        fake_user = SimpleNamespace(hashid="abcde")
        api_key = token_utils.generate_api_secret(fake_user)
        assert api_key.startswith("abcde-")

    def test_notification_mailer_send_renders_and_delivers(self, testapp, monkeypatch):
        called = {}

        def fake_deliver_now(self, to_emails, subject, html_body, **kwargs):
            called["to"] = to_emails
            called["subject"] = subject
            called["html_body"] = html_body
            called["kwargs"] = kwargs
            return True

        monkeypatch.setattr(NotificationMailer, "deliver_now", fake_deliver_now)
        mailer = NotificationMailer("person@example.com", "Subject line", "Message body", link="https://example.com")

        with testapp.application.app_context():
            result = mailer.send()

        assert result is True
        assert called["to"] == "person@example.com"
        assert called["subject"] == "Subject line"
