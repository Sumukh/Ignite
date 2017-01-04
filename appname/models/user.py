import logging

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from appname.models import db, Model

logger = logging.getLogger(__name__)

class User(Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, email, password):
        self.email = email.lower().strip()
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    @property
    def is_authenticated(self):
        return not isinstance(self, AnonymousUserMixin)

    def is_anonymous(self):
        return isinstance(self, AnonymousUserMixin)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.email)
