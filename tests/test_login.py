import pytest

create_user = True

@pytest.mark.usefixtures("testapp")
class TestLogin:
    def test_login(self, testapp):
        """ Tests if the login form functions """

        rv = testapp.post('/login', data=dict(
            email='admin@example.com',
            password="supersafepassword"
        ), follow_redirects=True)

        assert rv.status_code == 200
        assert 'Logged in successfully.' in str(rv.data)

    def test_login_bad_email(self, testapp):
        """ Tests if the login form rejects invalid email """

        rv = testapp.post('/login', data=dict(
            email='admin',
            password=""
        ), follow_redirects=True)

        assert rv.status_code == 200
        assert 'Invalid email address' in str(rv.data)

    def test_login_bad_password(self, testapp):
        """ Tests if the login form fails correctly """

        rv = testapp.post('/login', data=dict(
            email='admin@example.com',
            password="notsafepassword"
        ), follow_redirects=True)

        assert rv.status_code == 200
        assert 'Invalid email or password' in str(rv.data)
