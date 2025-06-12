import os

from integrations import login_client

_cached_okapi_token = None
_cached_eureka_token = None


def get_okapi_token():
    global _cached_okapi_token
    if _cached_okapi_token:
        return _cached_okapi_token

    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    _cached_okapi_token = __login(username, password)
    return _cached_okapi_token


def get_eureka_token():
    global _cached_eureka_token
    if _cached_eureka_token:
        return _cached_eureka_token

    username = os.getenv("EUREKA_ADMIN_USERNAME")
    password = os.getenv("EUREKA_ADMIN_PASSWORD")
    _cached_eureka_token = __login(username, password)
    return _cached_eureka_token


def __login(username: str, password: str):
    return login_client.login_as_admin(username, password)
