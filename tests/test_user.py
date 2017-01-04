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

        admin = User('admin@example.com', 'supersafepassword')
        db.session.add(admin)
        db.session.commit()

        user = User.query.filter_by(email="admin@example.com").first()
        assert user is not None

    def test_user_password(self, testapp):
        """ Test password hashing and checking """

        admin = User('admin@example.com', 'supersafepassword')

        assert admin.email == 'admin@example.com'
        assert admin.check_password('supersafepassword')
