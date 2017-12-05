""" This file defines utilities used to enforce user roles. """
from flask import current_user
from functools import wraps
from enum import Enum

class Roles(Enum):
    GUEST = 'guest'
    USER = 'user'
    ADMIN = 'admin'

def requires_roles(*roles):
    def wrapper(f):
        def get_user_role():
            if current_user.is_anonymous:
                return Roles.guest
            return current_user.role

        @wraps(f)
        def wrapped(*args, **kwargs):
            if get_user_role() not in roles:
                raise
            return f(*args, **kwargs)
        return wrapped
    return wrapper
