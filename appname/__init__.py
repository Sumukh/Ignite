#! ../env/bin/python

from flask import Flask
from webassets.loaders import PythonLoader as PythonAssetsLoader

from appname import assets
from appname.models import db
from appname.api.resources import api_blueprint
from appname.controllers.main import main
from appname.controllers.auth import auth
from appname.controllers.dashboard import dashboard
from appname.controllers.oauth.client import oauth_client
from appname.controllers.admin.jobs import jobs

from appname.extensions import (
    admin,
    assets_env,
    cache,
    debug_toolbar,
    login_manager,
    mail,
    rq2,
    socketio,
    token
)

def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. appname.settings.ProdConfig
    """

    app = Flask(__name__)

    app.config.from_object(object_name)

    # initialize the cache
    cache.init_app(app)

    # initialize the debug tool bar
    debug_toolbar.init_app(app)

    # initialize SQLAlchemy
    db.init_app(app)

    # initalize Flask Login 
    login_manager.init_app(app)

    # initialize Flask-RQ2 (job queue)
    rq2.init_app(app)

    token.init_app(app)
    mail.init_app(app)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # register our blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(oauth_client, url_prefix='/oauth')

    # Admin Tools 
    app.register_blueprint(jobs, url_prefix='/admin/rq')
    admin.init_app(app)

    # If you use websockets/realtime features
    # socketio.init_app(app)

    return app
