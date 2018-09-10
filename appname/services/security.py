import hashlib
from itsdangerous import URLSafeTimedSerializer

class Token:
    def init_app(self, app):
        self.app = app
        encoded_secret = app.config["SECRET_KEY"].encode()
        self.ts = URLSafeTimedSerializer(encoded_secret)
        self.unique_salt = hashlib.md5(encoded_secret).hexdigest()[:5]

    def generate(self, key, salt='default-salt'):
        return self.ts.dumps(key, salt + self.unique_salt)

    def decode(self, token, salt='default-salt', max_age=86400):
        """ Either converts a token into the original value or raises an Exception. """
        return self.ts.loads(token, salt=salt + self.unique_salt, max_age=86400)
