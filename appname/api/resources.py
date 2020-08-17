from flask import redirect, url_for

from appname.api import api, api_blueprint, API_VERSION, API_BASE
from appname.api.info import APIInfo

@api_blueprint.record
def record_params(setup_state):
    """ Load used app configs into local config on registration from
    appname/__init__.py """
    app = setup_state.app
    api_blueprint.config['tz'] = app.config.get('TIMEZONE', 'utc')  # sample config
    api_blueprint.config['debug'] = app.debug

@api_blueprint.route('/')
def home():
    return redirect(url_for('api.apiinfo'))

api.add_resource(APIInfo, '/{0}/info'.format(API_VERSION))
