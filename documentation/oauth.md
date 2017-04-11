OAuth is backed by oauthlib and Flask-OAuth: https://pythonhosted.org/Flask-OAuth/

# Providers

Google
```
provider_auth = oauth.remote_app(
    'google',
    app_key='GOOGLE',
    request_token_params={
        'scope': 'email',
        'state': lambda: security.gen_salt(10),
        'prompt': 'select_account'
    },
    base_url='https://www.googleapis.com/plus/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

def user_from_token(token):
    # Make a request to base_url/user to get user_info
    response = provider_auth.get('people/me')
    if response.status == 200:
        user_data = response.data

        if 'error' not in data and user_data.get('emails'):
            email = user_data['emails'][0]['value']
            return User.lookup_or_create(email)
    flash("We could not log you in. Try again soon", 'warning')
    return redirect('/')

```

OKPY
```
provider_auth = oauth.remote_app(
    'ok-server',  # Server Name
    consumer_key='example',
    consumer_secret='your-secret-here',
    request_token_params={'scope': 'email',
                          'state': lambda: security.gen_salt(10)},
    base_url='https://okpy.org/api/v3/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://okpy.org/oauth/token',
    authorize_url='https://okpy.org/oauth/authorize'
)

def user_from_token(token):
    # Make a request to base_url/user to get user_info
    response = provider_auth.get('user')
    if response.status == 200:
        user_data = response.data
        email = user_data['data']['email']
        return User.lookup_or_create(email)
    else:
        flash("We could not log you in. Try again soon", 'warning')
        return redirect('/')

```