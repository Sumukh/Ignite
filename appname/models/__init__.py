import functools
import json
import logging

from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
logger = logging.getLogger(__name__)

# Want to keep track of changes to your models? SQLAlchemy-Continuum will help!

class QueryWithSoftDelete(BaseQuery):
    """ By default, use soft deletes. See this blog post for usage details:
    https://blog.miguelgrinberg.com/post/implementing-the-soft-delete-pattern-with-flask-and-sqlalchemy
    Source: https://github.com/miguelgrinberg/sqlalchemy-soft-delete/blob/master/app.py
    License: MIT License
    """
    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(deleted=False) if not with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(db.class_mapper(self._mapper_zero().class_),
                              session=db.session(), _with_deleted=True)

    def _get(self, *args, **kwargs):
        # this calls the original query.get function from the base class
        return super(QueryWithSoftDelete, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        # the query.get method does not like it if there is a filter clause
        # pre-loaded, so we need to implement it using a workaround
        obj = self.with_deleted()._get(*args, **kwargs)
        return obj if obj is not None and not obj.deleted else None


class Model(db.Model):
    """ Add a timestamp to all models and allow for serialization."""
    __abstract__ = True

    created = db.Column(db.DateTime(timezone=True),
                        server_default=db.func.now(), nullable=False)
    deleted = db.Column(db.Boolean(), default=False)

    query_class = QueryWithSoftDelete

    GDPR_EXPORT_COLUMNS = {}

    def __repr__(self):
        if hasattr(self, 'id'):
            key_val = self.id
        else:
            pk = self.__mapper__.primary_key
            if isinstance(pk, tuple):
                key_val = pk[0].name
            else:
                key_val = self.__mapper__.primary_key._list[0].name
        return '<{0} {1}>'.format(self.__class__.__name__, key_val)

    def delete(self, force=False):
        """ if force is called - it removes it from the database.
        Otherwise - performs a soft delete.
        """
        if force and self.can_be_destroyed:
            db.session.delete(self)
            return db.session.commit()
        if force and not self.can_be_destroyed:
            logger.warning('Model {0} is not able to be force deleted'.format(self))
            raise Exception('Cannot force destroy {0}'.format(self))
        self.deleted = True
        return db.session.commit()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def from_dict(self, dict):
        for c in self.__table__.columns:
            if c.name in dict:
                setattr(self, c.name, dict[c.name])
        return self

    def gdpr_export_pii_data(self):
        export = {}
        for key in self.GDPR_EXPORT_COLUMNS:
            value = getattr(self, key)
            try:
                json.dumps(value)
            except TypeError:
                # The object is not json serializable
                value = str(value)
            export[key] = value

        return export

    @property
    def can_be_destroyed(self):
        # Is it ok to truly delete this model (for GDPR deletion requests)
        return True

    @classmethod
    def get_by_hashid(self, hashid):
        from appname.extensions import hashids
        return self.get(hashids.decode_id(hashid))

    @property
    def hashid(self):
        from appname.extensions import hashids
        return hashids.encode_id(self.id)

class ModelProxy:
    """ A singleton that lazily imports models to handle
    circular import dependencies.
    Usage: ModelProxy.Model.query
    """

    def __getattribute__(self, key):
        import appname.models
        return appname.models.__getattribute__(key)


ModelProxy = ModelProxy()

def transaction(f):
    """ Decorator for database (session) transactions."""
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        try:
            value = f(*args, **kwds)
            db.session.commit()
            return value
        except:  # noqa; This is intentional to ensure we rollback
            db.session.rollback()
            raise
    return wrapper
