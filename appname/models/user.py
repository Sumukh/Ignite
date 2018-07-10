import logging

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from appname.models import db, Model

logger = logging.getLogger(__name__)

class User(Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String())
    admin = db.Column(db.Boolean())
    role = db.Column(db.String(), default='user')
    email_confirmed = db.Column(db.Boolean())

    def __init__(self, email=None, password=None, admin=False, email_confirmed=False):
        if not email:
            raise ValueError('No Email Provided')

        self.email = email.lower().strip()
        self.email_confirmed = email_confirmed

        if admin:
            self.admin = True
            self.role = 'admin'  # TODO: Clean this up

        if password:
            self.set_password(password)

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

    def __repr__(self):
        return '<User {0}>'.format(self.email)

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def lookup_or_create(cls, email, **kwargs):
        existing = cls.query.filter_by(email=email).first()
        if existing:
            return existing
        new_user = User(email=email, **kwargs)
        db.session.add(new_user)
        db.session.commit()
        return new_user
