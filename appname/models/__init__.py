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

    def __repr__(self):
        if hasattr(self, 'id'):
            key_val = self.id
        else:
            pk = self.__mapper__.primary_key
            if type(pk) == tuple:
                key_val = pk[0].name
            else:
                key_val = self.__mapper__.primary_key._list[0].name
        return '<{0} {1}>'.format(self.__class__.__name__, key_val)

    def delete(self, force=False):
        """ if force is called - it removes it from the database.
        Otherwise - performs a soft delete.
        """
        if force:
            db.session.delete(self)
        else:
            self.deleted = True
            db.session.commit()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def from_dict(self, dict):
        for c in self.__table__.columns:
            if c.name in dict:
                setattr(self, c.name, dict[c.name])
        return self

class ModelProxy:
    """ A singleton that lazily imports models to handle
    circular import dependencies.
    Usage: ModelProxy.Model.query
    """
    def __getattribute__(self, key):
        import appname.models
        return appname.models.__getattribute__(key)

ModelProxy = ModelProxy()
