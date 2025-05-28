import dotenv
import requests

from utils import env, log_factory

_log = log_factory.get_logger(__name__)
dotenv.load_dotenv()


def login_as_admin(username, password):
    """Get the admin token from Okapi."""
    tenant_id = env.get_tenant_id()
    _log.info(f"Requesting admin token from Okapi [tenantId='{tenant_id}']...")
    headers = {
        'Content-Type': 'application/json',
        'X-Okapi-Tenant': env.get_tenant_id(),
    }

    data = {
        'username': username,
        'password': password
    }

    response = requests.post(
        url=f"{env.get_okapi_url()}/authn/login-with-expiry",
        json=data, headers=headers)

    if response.status_code == 201:
        cookie_headers = response.headers.get("Set-Cookie")
        for cookie in cookie_headers.split(";"):
            if cookie.startswith("folioAccessToken"):
                access_token = cookie.split("=")[1]
                _log.info(f"Admin token is requested.")
                return access_token
            else:
                _log.error(f"Failed to find admin token in cookies: folioAccessToken not found")
                raise Exception("folioAccessToken cookie not found.")
    else:
        _log.error(f"Failed to get admin token: {response.status_code} {response.text}")
        raise Exception(f"Failed to get admin token: {response.status_code} {response.text}")
