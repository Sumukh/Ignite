import os
import pytest

# ProdConfig reads DATABASE_URL at import time. Ensure tests always have a valid URL.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from appname import create_app
from appname.models import db
from appname.models.user import User

@pytest.fixture()
def testapp(request):
    app = create_app('appname.settings.TestConfig')
    client = app.test_client()

    db.app = app
    app_ctx = app.app_context()
    app_ctx.push()
    db.create_all()

    if getattr(request.module, "create_user", True):
        admin = User('admin@example.com', 'supersafepassword', admin=True)
        user = User('user@example.com', 'safepassword')
        db.session.add_all([admin, user])
        db.session.commit()

    def teardown():
        db.session.remove()
        db.drop_all()
        app_ctx.pop()

    request.addfinalizer(teardown)

    return client
