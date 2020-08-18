# Constants
import os

REQUIRE_EMAIL_CONFIRMATION = True
ALLOW_SIGNUPS = True
ALLOW_PASSWORD_LOGIN = True

# TODO: These shouldn't be in constants (should be in settings)
EMAIL_CONFIRMATION_SALT = os.getenv('EMAIL_CONFIRMATION_KEY', 'email-confirmation-key')
PASSWORD_RESET_SALT = os.getenv('PASSWORD_RESET_KEY', 'pass-reset-key')
PURCHASE_LICENSE_SALT = os.getenv('PASSWORD_RESET_KEY', 'license-purchase-key')


PASSWORD_RESET_VALIDITY_SECONDS = 86400

TEAM_MEMBER_ROLES = ['team member', 'administrator']
SUPPORT_EMAIL = os.getenv('HELP_EMAIL', 'help@example.com')
MAX_TEAM_SIZE = 50