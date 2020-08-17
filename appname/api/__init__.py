from flask import Blueprint, request, jsonify

from flask_restful.representations.json import output_json
from flask_restful import reqparse, fields, abort
import flask_restful as restful

from appname.extensions import login_manager
from appname.models.user import User

api_blueprint = Blueprint('api', __name__)
api_blueprint.config = {}

api = restful.Api(api_blueprint)

API_VERSION = 'v1'
API_BASE = '/'  # API_BLUEPRINT prefix is 'api'

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

@login_manager.request_loader
def load_user_from_request(request):
    # Only functional for API Endpoints
    if not request.endpoint or not request.endpoint.startswith("api."):
        return None

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if not api_key:
        return None
    user_id, _ = api_key.split('-')
    user = User.get_by_hashid(user_id)
    if user and user.check_api_key_hash(api_key):
        return user

def custom_abort(status_code, message, data=None):
    response = jsonify({
        'code': status_code,
        'data': data,
        'message': message,
    })
    response.status_code = status_code
    return response

def handle_api_error(err):
    return custom_abort(404, str(err))

class Resource(restful.Resource):
    method_decorators = []
    required_scopes = {}
    # applies to all inherited resources

    def __repr__(self):
        return "<Resource {0}>".format(self.__class__.__name__)

    def make_response(self, data, *args, **kwargs):
        return super().make_response(data, *args, **kwargs)


class BaseAPISchema():
    """ APISchema describes the input and output formats for
    resources. The parser deals with arguments to the API.
    The API responses are marshalled to json through get_fields
    """
    get_fields = {}

    def __init__(self):
        self.parser = reqparse.RequestParser()

    def parse_args(self):
        return self.parser.parse_args()

