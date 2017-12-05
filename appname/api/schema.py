from flask_restful import reqparse, fields

class APISchema():
    """ APISchema describes the input and output formats for
    resources. The parser deals with arguments to the API.
    The API responses are marshalled to json through get_fields
    """
    get_fields = {
        'id': fields.Integer,
        'created': fields.DateTime(dt_format='iso8601')
    }

    def __init__(self):
        self.parser = reqparse.RequestParser()

    def parse_args(self):
        return self.parser.parse_args()


class APISchema(APISchema):
    get_fields = {
        'version': fields.String,
        'url': fields.String,
        'documentation': fields.String
    }
