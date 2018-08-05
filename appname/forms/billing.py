from appname.forms import BaseForm
from wtforms import validators, TextField, HiddenField, SelectField

from appname.models.billing import ProductPlan

class FreeSubscriptionForm(BaseForm):
    plan_id = HiddenField('Plan ID')

    def validate(self):
        check_validate = super(FreeSubscriptionForm, self).validate()
        if not check_validate:
            return False

        plan = ProductPlan.get_by_hashid(self.plan_id.data)
        if not plan:
            return False

        if not plan.is_free_plan:
            return False

        return True