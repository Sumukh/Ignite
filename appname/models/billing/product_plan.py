import logging

from appname.models import db, Model
from appname.models.user import User

from appname.utils.token import url_safe_token

logger = logging.getLogger(__name__)

class ProductPlan(Model):
    id = db.Column(db.Integer(), primary_key=True)

    stripe_plan_id = db.Column(db.String(), nullable=True)
    stripe_product_id = db.Column(db.String(), nullable=True)

    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())

    public = db.Column(db.Boolean(), default=True)
    trial_seconds = db.Column(db.Integer(), default=(60*60*24*14))
    tax_percent = db.Column(db.Float(), default=0.0)

    # TODO: Check if the user has a subscription

    @property
    def is_free_plan(self):
        return self.stripe_product_id is None