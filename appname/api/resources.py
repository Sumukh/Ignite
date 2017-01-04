from appname.api import api, api_blueprint, API_VERSION
from appname.api.info import APIInfo

@api_blueprint.record
def record_params(setup_state):
    """ Load used app configs into local config on registration from
    appname/__init__.py """
    app = setup_state.app
    api_blueprint.config['tz'] = app.config.get('TIMEZONE', 'utc')  # sample config
    api_blueprint.config['debug'] = app.debug

API_BASE = '/'  # API_BLUEPRINT prefix is 'api'
api.add_resource(APIInfo, API_BASE, '/{0}/'.format(API_VERSION))
