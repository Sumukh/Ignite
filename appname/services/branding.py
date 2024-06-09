import os
class Branding:
    def __init__(self):
        self.environment = "prod"
        self.config = {}

    def init_app(self, app):
        self.config  = app.config
        self.environment = app.config.get('ENV', 'prod')

    @property
    def name(self):
        if self.environment == "dev":
            return "appname-dev"
        return "appname"

    @property
    def support_email(self):
        email = self.config.get('support_email', 'help@example.com')
        return email

    @property
    def icon_path(self):
        return "public/ignite/ignite-logo@2x.png"

    @property
    def website_domain(self):
        return "appname.com"

    @property
    def legal_name(self):
        return "appname.com"

    @property
    def corporate_jurisdiction(self):
        return "United States"

    @property
    def full_logo_path(self):
        return "public/ignite/ignite-logo@2x.png"

