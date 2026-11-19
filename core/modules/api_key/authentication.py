from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .services import find_valid_key


class ApiKeyAuthentication(BaseAuthentication):
    ## authenticate(): no Authorization: Bearer ... header → None;
    ## call find_valid_key(); no key → raise AuthenticationFailed("Invalid or revoked API key.");
    ## valid → return (caller, key)
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        parts = header.split()
        if not parts or parts[0].lower() != "bearer":
            return None
        if len(parts) != 2:
            raise AuthenticationFailed("Invalid Authorization header.")
        key = find_valid_key(parts[1])
        if key is None:
            raise AuthenticationFailed("Invalid or revoked API key.")
        return (ApiKeyCaller(key), key)

    def authenticate_header(self, request):
        return "Bearer"

class ApiKeyCaller:
    """The identity behind an API key request: a server, not a human user."""
    is_authenticated = True
    is_anonymous = False

    def __init__(self, api_key):
        self.api_key = api_key
        self.project = api_key.project
        self.pk = f"apikey:{api_key.pk}"    # a unique id, e.g. for per-key rate limiting later

    def __str__(self):
        return f"ApiKey {self.api_key.prefix} (project {self.project.pk})"
