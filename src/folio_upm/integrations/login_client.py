import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.utils import env, log_factory

_log = log_factory.get_logger(__name__)


class LoginClient(metaclass=SingletonMeta):

    def __init__(self):
        """Initialize the LoginClient."""
        _log.debug("LoginClient initialized.")

    @staticmethod
    def login_as_admin(base_url: str, username: str, password: str) -> str:
        """Get the admin token from Okapi."""
        _log.info("Requesting admin token from Okapi...")
        headers = {
            "Content-Type": "application/json",
            "X-Okapi-Tenant": env.get_tenant_id(),
        }

        response = requests.post(
            url=f"{env.get_okapi_url()}/authn/login-with-expiry",
            json={"username": username, "password": password},
            headers=headers,
        )

        if response.status_code == 201:
            cookie_headers = response.headers.get("Set-Cookie")
            for cookie in cookie_headers.split(";"):
                if cookie.startswith("folioAccessToken"):
                    access_token = cookie.split("=")[1]
                    _log.info("Admin token is requested.")
                    return access_token
                else:
                    _log.error("Failed to find admin token in cookies")
                    raise Exception("folioAccessToken cookie not found.")
        else:
            error_msg = f"Failed to get admin token: {response.status_code} {response.text}"
            _log.error(error_msg)
            raise Exception(error_msg)
