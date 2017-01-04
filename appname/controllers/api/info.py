from flask_restful import marshal_with

from appname.controllers.api import Resource, API_VERSION
from appname.controllers.api.schema import APISchema

class APIInfo(Resource):
    schema = APISchema()

    @marshal_with(schema.get_fields)
    def get(self):
        return {
            'version': API_VERSION,
            'url': '/api/{0}/'.format(API_VERSION),
            'documentation': ''
        }
