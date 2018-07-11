import base64
import uuid

# Python 3.6+ would allow us to do
# >>> import secrets
# >>> secrets.token_urlsafe(8)
# 'Pxym7N2zJRs'

def url_safe_token():
    base64token = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return (base64token.decode('utf-8').replace('=', '').
            replace('-', '').replace('_', '')[0:9])
