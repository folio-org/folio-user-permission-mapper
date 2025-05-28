import os
from integrations import login_client

_cached_token = None


def get_admin_token():
    global _cached_token
    if _cached_token:
        return _cached_token

    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    _cached_token = login_client.login_as_admin(username, password)
    return _cached_token
