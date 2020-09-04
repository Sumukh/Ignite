# If you want to silence some the inital ExtDeprecationWarning warnings
# import warnings
# from flask.exthook import ExtDeprecationWarning
# warnings.simplefilter('ignore', ExtDeprecationWarning)
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_assets import Environment
# from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
from flask_rq2 import RQ
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from raven.contrib.flask import Sentry
from flask_cloudy import Storage

from appname.admin import AdminDashboard
from appname.services.security import Token
from appname.services.stripe import Stripe
from appname.services.hash_ids import HashIds

# Setup flask cache
cache = Cache()

# init flask assets
assets_env = Environment()

debug_toolbar = DebugToolbarExtension()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"
# login_manager.user_loader is registered in controllers/auth.

# TODO:
login_manager.refresh_view = "auth.reauth"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

token = Token()

# socketio = SocketIO()
rq2 = RQ()
admin = AdminDashboard()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
stripe = Stripe()
sentry = Sentry()
hashids = HashIds()
storage = Storage()
