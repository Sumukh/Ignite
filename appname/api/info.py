from flask_restful import marshal_with
from flask_login import current_user
from appname.api import Resource, API_VERSION
from appname.api.schema import APISchema

class APIInfo(Resource):
    schema = APISchema()

    @marshal_with(schema.get_fields)
    def get(self):
        return {
            'version': API_VERSION,
            'url': '/api/{0}/info'.format(API_VERSION),
            'authenticated': current_user.is_authenticated,
            'user': current_user.email if current_user.is_authenticated else None,
            'documentation': ''
        }
