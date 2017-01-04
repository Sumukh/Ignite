from appname.controllers.api import api, api_blueprint
from appname.controllers.api.info import APIInfo

@api_blueprint.record
def record_params(setup_state):
    """ Load used app configs into local config on registration from
    appname/__init__.py """
    app = setup_state.app
    api_blueprint.config['tz'] = app.config.get('TIMEZONE', 'utc')  # sample config
    api_blueprint.config['debug'] = app.debug

api.add_resource(APIInfo, '/')
