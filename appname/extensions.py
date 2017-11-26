# If you want to silence some the inital ExtDeprecationWarning warnings
import warnings
from flask.exthook import ExtDeprecationWarning
warnings.simplefilter('ignore', ExtDeprecationWarning)

from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_assets import Environment
from flask_socketio import SocketIO
from flask_rq2 import RQ
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from appname.admin import AdminDashboard
from appname.security import Token
from appname.stripe_extension import Stripe

# Setup flask cache
cache = Cache()

# init flask assets
assets_env = Environment()

debug_toolbar = DebugToolbarExtension()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
# login_manager.user_loader is registered in controllers/auth.

# TODO:
login_manager.refresh_view = "auth.reauth"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

token = Token()

socketio = SocketIO()
rq2 = RQ()
admin = AdminDashboard()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
stripe = Stripe()
