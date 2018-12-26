import logging

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils.types import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import FernetEngine

from appname.models import db, Model, ModelProxy, global_encryption_key_iv

logger = logging.getLogger(__name__)

class User(Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String())
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String())
    admin = db.Column(db.Boolean())
    role = db.Column(db.String(), default='user')
    email_confirmed = db.Column(db.Boolean())

    # Encrypted Secret (used for Two Factor Authentication)
    encrypted_totp_secret = db.Column(EncryptedType(db.String,
                                                    key=global_encryption_key_iv,
                                                    engine=FernetEngine))

    GDPR_EXPORT_COLUMNS = {
        "hashid": "ID of User",
        "email": "User Email",
        "created": "When the user was created",
        "email_confirmed": "Whether the email was confirmation"
    }

    def __init__(self, email=None, password=None, admin=False,
                 email_confirmed=False, team=None):
        if not email:
            raise ValueError('No Email Provided')

        self.email = email.lower().strip()
        self.email_confirmed = email_confirmed

        if admin:
            self.admin = True
            self.role = 'admin'  # TODO: Clean this up

        if password:
            self.set_password(password)

        if not team:
            team_name = "{0}'s team".format(email)
            ModelProxy.teams.Team.create(team_name, self)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    @property
    def is_authenticated(self):
        return not isinstance(self, AnonymousUserMixin)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_anonymous(self):
        return isinstance(self, AnonymousUserMixin)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    @property
    def active_memberships(self):
        return [member for member in self.memberships if member.activated]

    @property
    def active_teams(self):
        return [member.team for member in self.active_memberships]

    # TODO: Cache
    @property
    def primary_membership_id(self):
        if len(self.active_memberships) == 0:
            return None
        return self.active_memberships[0].id

    def __repr__(self):
        return '<User {0}>'.format(self.email)

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def lookup_or_create_by_email(cls, email, **kwargs):
        existing = cls.query.filter_by(email=email).first()
        if existing:
            return existing
        new_user = User(email=email, **kwargs)
        db.session.add(new_user)
        db.session.commit()
        return new_user
