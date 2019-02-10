from werkzeug.routing import BaseConverter, ValidationError

from appname.extensions import hashids

class BoolConverter(BaseConverter):
    def __init__(self, url_map, false_value, true_value):
        super(BoolConverter, self).__init__(url_map)
        self.false_value = false_value
        self.true_value = true_value
        self.regex = '(?:{0}|{1})'.format(false_value, true_value)

    def to_python(self, value):
        return value == self.true_value

    def to_url(self, value):
        return self.true_value if value else self.false_value

class HashidConverter(BaseConverter):
    def to_python(self, value):
        try:
            return hashids.decode_id(value)
        except (TypeError, ValueError) as e:
            raise ValidationError(str(e))

    def to_url(self, value):
        return hashids.encode_id(value)

class CustomConverters:
    def init_app(self, app):
        app.url_map.converters['hashid'] = HashidConverter
        app.url_map.converters['bool'] = BoolConverter


custom_converters = CustomConverters()
