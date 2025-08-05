import requests

from folio_upm.model.cls_support import SingletonMeta
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class LoginClient(metaclass=SingletonMeta):

    def __init__(self):
        """Initialize the LoginClient."""
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LoginClient initialized.")

    def login_as_admin(self, base_url: str, username: str, password: str) -> str:
        """Get the admin token from Okapi."""
        self._log.info("Requesting admin token for URL: %s...", base_url)
        headers = {
            "Content-Type": "application/json",
            "X-Okapi-Tenant": Env().get_tenant_id(),
        }

        response = requests.post(
            url=f"{base_url}/authn/login-with-expiry",
            json={"username": username, "password": password},
            headers=headers,
        )

        if response.status_code == 201:
            cookie_headers = response.headers.get("Set-Cookie")
            for cookie in cookie_headers.split(";"):
                if cookie.startswith("folioAccessToken"):
                    access_token = cookie.split("=")[1]
                    self._log.info("Admin token is requested.")
                    return access_token
                else:
                    self._log.error("Failed to find admin token in cookies")
                    raise Exception("folioAccessToken cookie not found.")
        else:
            error_msg = f"Failed to get admin token: {response.status_code} {response.text}"
            self._log.error(error_msg)
            raise Exception(error_msg)
