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
        """Decode a token and return the original value or raise an Exception.

        Parameters
        ----------
        token : str
            Token to decode.
        salt : str, optional
            Salt used when generating the token. ``'default-salt'`` by default.
        max_age : int, optional
            Maximum age in seconds before the token expires. ``86400`` by
            default.
        """

        return self.ts.loads(token, salt=salt + self.unique_salt, max_age=max_age)
