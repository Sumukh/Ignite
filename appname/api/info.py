from flask_restful import marshal_with
from flask_restful import fields

from appname.api import Resource, BaseAPISchema, API_VERSION

class APISchema(BaseAPISchema):
    get_fields = {
        'version': fields.String,
        'url': fields.String,
        'documentation': fields.String,
    }


class APIInfo(Resource):
    schema = APISchema()

    @marshal_with(schema.get_fields)
    def get(self):
        return {
            'version': API_VERSION,
            'url': '/api/{0}/info'.format(API_VERSION),
            'documentation': 'Add api_key as a URL query parameter to authenticate'
        }
