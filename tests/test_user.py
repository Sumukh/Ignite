#! ../env/bin/python
# -*- coding: utf-8 -*-

import pytest

from appname.models import db
from appname.models.user import User

create_user = False


@pytest.mark.usefixtures("testapp")
class TestModels:
    def test_user_save(self, testapp):
        """ Test Saving the user model to the database """

        user = User('user@example.com', 'supersafepassword')
        db.session.add(user)
        db.session.commit()

        user_obj = User.query.filter_by(email="user@example.com").first()
        assert user_obj is not None
        assert not user_obj.is_admin

    def test_user_password(self, testapp):
        """ Test password hashing and checking """

        admin = User('admin@example.com', 'supersafepassword', admin=True)

        assert admin.email == 'admin@example.com'
        assert admin.email == 'admin@example.com'
        assert admin.check_password('supersafepassword')
        assert admin.is_admin
