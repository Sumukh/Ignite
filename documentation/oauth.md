OAuth is backed by Flask-Dance

## Setup

## Providers

### Google

#### Configuration:

* Get API Keys here: https://console.developers.google.com/apis/credentials
* Add "http://localhost:5000/oauth/google/authorized" and "https://[your production website]/oauth/google/authorized" to the authorized redirects

Make sure you set the following environment variables so that you can try this locally.

```
export OAUTHLIB_INSECURE_TRANSPORT=1 # To allow local logins without having to use  HTTPs locally
export GOOGLE_CONSUMER_KEY='your-code.apps.googleusercontent.com'
export GOOGLE_CONSUMER_SECRET='your-secret'
```

#### Implementation:

See `appname/controllers/google.py`.


### Other Providers (Github, Slack, Twitter, etc)

Add similiar blueprints for each one. Reference the [Flask-Dance](https://flask-dance.readthedocs.io/en/latest/) documentation. We use the SQLAlchemy storage backend.

### Custom Provider
```
from flask import Flask
from flask_dance.consumer import OAuth2ConsumerBlueprint

example_blueprint = OAuth2ConsumerBlueprint(
    "ok-server", __name__,
    client_id="my-key-here",
    client_secret="my-secret-here",
    base_url="https://okpy.org/api/v3/",
    token_url="https://okpy.org/oauth/token",
    authorization_url="https://okpy.org/oauth/authorize,
    scope='email',
    # state=lambda: security.gen_salt(10),

# The rest would be similiar to `google.py` but you'd have to update the API endpoints.



