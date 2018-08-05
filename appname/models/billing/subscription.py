import logging

from appname.models import db, Model
from appname.models.user import User

from appname.utils.token import url_safe_token

logger = logging.getLogger(__name__)

class StripeSubscription(Model):
    id = db.Column(db.Integer(), primary_key=True)
    team_id = db.Column(db.ForeignKey("team.id"), index=True,
                        nullable=False)

    product_plan_id = db.Column(db.ForeignKey("product_plan.id"))

    # It's possible to associate multiple plans with the
    # same stripe subscription id. To do that, you'll need to
    # create a join table on ProductPlans & StripeSubcription.
    # https://stripe.com/docs/billing/subscriptions/multiplan
    stripe_subscription_id = db.Column(db.String())
    stripe_customer_id = db.Column(db.String())

    active = db.Column(db.Boolean())

    team = db.relationship("Team", backref="subscription")
    product_plan = db.relationship("ProductPlan", backref='subscriptions')

    @property
    def is_billable(self):
        # Should we exepect recurring revenue from this subscription?
        return self.stripe_subscription_id != None and self.active