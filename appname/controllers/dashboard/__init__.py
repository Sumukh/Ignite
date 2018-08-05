from .home import blueprint as home_blueprint
from .settings import blueprint as settings_blueprint
from .team import blueprint as team_blueprint
from .billing import blueprint as billing_blueprint

dashboard_blueprints = [
    home_blueprint,
    settings_blueprint,
    team_blueprint,
    billing_blueprint
]