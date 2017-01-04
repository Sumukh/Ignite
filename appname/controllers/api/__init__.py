from flask import Blueprint, request
from flask_restful.representations.json import output_json

import flask_restful as restful

api_blueprint = Blueprint('api', __name__)
api_blueprint.config = {}

api = restful.Api(api_blueprint)

API_VERSION = 'v1'

@api.representation('application/json')
def envelope_api(data, code, headers=None):
    """ API response envelope (for metadata/pagination).
    Optionally wraps JSON response in envelope.
    This is for successful requests only.

        data is the object returned by the API.
        code is the HTTP status code as an int
    """
    if not request.args.get('envelope'):
        return output_json(data, code, headers)
    message = 'success'
    if 'message' in data:
        message = data['message']
        del data['message']
    data = {
        'data': data,
        'code': code,
        'message': message
    }
    return output_json(data, code, headers)

class Resource(restful.Resource):
    method_decorators = []
    required_scopes = {}
    # applies to all inherited resources

    def __repr__(self):
        return "<Resource {0}>".format(self.__class__.__name__)

    def make_response(self, data, *args, **kwargs):
        return super().make_response(data, *args, **kwargs)
