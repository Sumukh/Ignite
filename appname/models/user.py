import logging

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy_utils.types import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import FernetEngine

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from appname.models import db, Model, ModelProxy, global_encryption_key_iv

logger = logging.getLogger(__name__)

# (Ignite) TODO: Cleanup the methods here

class User(Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String())
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String())
    admin = db.Column(db.Boolean())
    role = db.Column(db.String(), default='user')
    email_confirmed = db.Column(db.Boolean())
    user_api_key_hash = db.Column(db.String())
    billing_customer_id = db.Column(db.String())

    # Encrypted Secret (used for Two Factor Authentication)
    encrypted_totp_secret = db.Column(EncryptedType(db.String,
                                                    key=global_encryption_key_iv,
                                                    engine=FernetEngine))

    GDPR_EXPORT_COLUMNS = {
        "id": "ID of the user",
        "hashid": "ID of User",
        "email": "User Email",
        "created": "When the user was created",
        "full_name": "The users full name",
        "email_confirmed": "Whether the email was confirmation"
    }

    # TODO: Refactor out our override of __init__. It should either be a 
    # seperate function or a class method. 
    def __init__(self, email=None, password=None, admin=False,
                 email_confirmed=False, team=None, name=None, 
                 deleted=False, role='user'):
        if not email:
            raise ValueError('No Email Provided')

        self.email = email.lower().strip()
        self.full_name = name
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

    def check_api_key_hash(self, api_key):
        # Potential timing attack here
        if self.user_api_key_hash:
            return check_password_hash(self.user_api_key_hash, api_key)
        return False

    def hash_api_key(self, api_key):
        self.user_api_key_hash = generate_password_hash(api_key)
        db.session.add(self)
        db.session.commit()

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
    def admin_memberships(self):
        return [member for member in self.memberships if member.activated and member.role == 'administrator']

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

class OAuth(Model, OAuthConsumerMixin):
    __table_args__ = (db.UniqueConstraint("provider", "provider_user_id"),)
    provider_user_id = db.Column(db.String(256), nullable=False)
    provider_user_login = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(
        User,
        # This `backref` thing sets up an `oauth` property on the User model,
        # which is a dictionary of OAuth models associated with that user,
        # where the dictionary key is the OAuth provider name.
        backref=db.backref(
            "oauth",
            collection_class=attribute_mapped_collection("provider"),
            cascade="all, delete-orphan",
        ),
    )
    GDPR_EXPORT_COLUMNS = {
        "provider_user_login": "Provider User Login",
        "provider_user_id": "Provider User ID ",
        "provider": "The provider",
        "created_at": "When it was created"
    }
