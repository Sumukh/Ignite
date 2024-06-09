class Branding:
    def __init__(self):
        self.environment = "prod"

    def init_app(self, app):
        self.environment = app.config.get('ENV', 'prod')

    @property
    def name(self):
        if self.environment == "dev":
            return "appname-dev"
        return "appname"

    @property
    def support_email(self):
        return "appname@example.com"

    @property
    def icon_path(self):
        return "public/ignite/ignite-logo@2x.png"

    @property
    def full_logo_path(self):
        return "public/ignite/ignite-logo@2x.png"

