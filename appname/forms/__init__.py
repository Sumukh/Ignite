from flask_wtf import FlaskForm
from wtforms import StringField

def strip_whitespace(value):
    if value and hasattr(value, "strip"):
        return value.strip()
    else:
        return value

class BaseForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get('filters', [])
            field_type = type(unbound_field)
            if field_type == StringField:
                filters.append(strip_whitespace)
            return unbound_field.bind(form=form, filters=filters, **options)


class SimpleForm(BaseForm):
    pass  # Used for forms that have no input (other than a CSRF check)
