import os
import logging

from appname.extensions import stripe
from appname.models import db, ModelProxy
logger = logging.getLogger(__name__)

METERED = 'metered_by_user'
UNLIMITED = 'unlimited'

class BasePlan:
    stripe_product_id = None
    name = None
    billing_type = UNLIMITED
    description = 'A plan for appname'
    friendly_name = "Default Plan"

    def __init__(self, team):
        self.team = team

    def set_team_plan(self):
        self.team.plan = self.name
        db.session.add(self.team)
        db.session.commit()

    @property
    def can_add_more_users(self):
        if self.billing_type == UNLIMITED:
            return True
        else:
            return False

    @property
    def has_access_to_feature_x(self):
        return False

    def record_change_in_usage(self):
        # If we are metered, we'd need to tell stripe about our new usage
        if self.billing_type == METERED:
            # Here we control the usage, so we can just report the final number to stripe
            all_subscription_items = stripe.all_subscription_items(self.team.subscription_id)
            subscription_items_for_this_plan = [s for s in all_subscription_items
                                                if s['product'] == self.stripe_product_id]
            if len(subscription_items_for_this_plan) < 1:
                logger.debug("Failed on subscription ID {}".format(self.team.subscription_id))
                raise Exception('Could not find billing for this product')
            subscription_item = subscription_items_for_this_plan[0]

            quantity = len(self.team.active_members)
            logger.debug("Setting subscription for team {} to {}".format(self.team.id, quantity))
            stripe.report_usage(subscription_item.id, quantity)

    @classmethod
    def is_free(cls):
        raise Exception('BaseClass does not implement')

    @classmethod
    def get_num_teams(cls, team):
        return ModelProxy.teams.Team.query.filter_by(plan=cls.name).count()

class FreePlan(BasePlan):
    stripe_product_id = None
    name = 'free'
    friendly_name = "Free Plan"
    description = 'The free plan'
    billing_type = METERED

    @classmethod
    def is_free(cls):
        return True

    @property
    def can_add_more_users(self):
        return len(self.team.members) < 5

class MonthlyPremium(BasePlan):
    stripe_product_id = os.getenv('STRIPE_MONTHLY_PREMIUM_ID', 'price_1HGzFQID8JASalnlgBAX2hjo')
    name = 'monthly_premium'
    billing_type = UNLIMITED
    friendly_name = "Premium (Monthly)"

    @classmethod
    def is_free(cls):
        return False

    @property
    def can_add_more_users(self):
        return True

class AnnualPremium(MonthlyPremium):
    stripe_product_id = os.getenv('STRIPE_ANNUAL_PREMIUM_ID', 'price_1HGzFQID8JASalnlBeRxlkno')
    name = 'annual_premium'
    friendly_name = "Premium (Annual)"

class MeteredPlan(BasePlan):
    stripe_product_id = os.getenv('STRIPE_METERED_PLAN_ID', 'price_1HGzFQID8JASalnlBeRxlkno')
    billing_type = METERED
    name = 'pay_as_you_go'
    friendly_name = "Pay as you Go"

    @classmethod
    def is_free(cls):
        return False

    @property
    def can_add_more_users(self):
        return True

free_plans = [FreePlan]
all_plans = [FreePlan, MonthlyPremium, AnnualPremium]
plans_by_name = {plan.name: plan for plan in all_plans}

# TODO: `stripe_product_id` is a confusing name, because this is actually a a price, for the same product
# We do this so we can distinguish between annual and monthly pricing
plans_by_price_id = {plan.stripe_product_id: plan for plan in all_plans}
