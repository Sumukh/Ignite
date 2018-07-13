import pytest

create_user = True

def expect_response(route, code, testapp):
    rv = testapp.get(route)
    assert rv.status_code == code

@pytest.mark.usefixtures("testapp")
class TestURLs:

    def test_home(self, testapp):
        """ Tests if the home page loads """
        expect_response('/', 200, testapp)

    def test_login(self, testapp):
        """ Tests if the login page loads """
        expect_response('/login', 200, testapp)

    def test_logout(self, testapp):
        """ Tests if the logout page redirects """
        expect_response('/auth/logout', 302, testapp)

    def test_signup(self, testapp):
        """ Tests if the logout page loads """
        expect_response('/signup', 200, testapp)

    def test_dashboard_logged_out(self, testapp):
        """ Tests if the restricted page returns a 302
            if the user is logged out
        """
        expect_response('/dashboard/', 302, testapp)

    def test_restricted_logged_in(self, testapp):
        """ Tests if the restricted page returns a 200
            if the user is logged in
        """
        testapp.post('/login', data=dict(
            email='admin@example.com',
            password="supersafepassword"
        ), follow_redirects=True)
        expect_response('/dashboard/', 200, testapp)
