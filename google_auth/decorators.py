from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from oauth2client.client import OAuth2Credentials


def auth_required(f):
    """Decorator to check credentials for google api."""
    @wraps(f)
    def _wrapper(*args, **kwargs):
        request = args[0]
        credentials_data = request.session.get(settings.CREDENTIALS_KEY)

        if credentials_data:
            credentials = OAuth2Credentials.from_json(credentials_data)
            if not credentials.access_token_expired:
                return f(request)

        return redirect('auth')

    return _wrapper
