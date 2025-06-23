from typing import Any, Callable, Optional

import requests

from folio_upm.utils import json_utils, log_factory
from folio_upm.utils.upm_env import Env


class HttpClient:

    def __init__(self, base_url: str, auth_func: Callable, client_timeout: int | None = None):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._base_url = base_url
        self._auth_func = auth_func
        self._timeout = client_timeout or Env().get_http_client_timeout()

    def get_json(self, path: str, params: dict | None = None, handle_404: bool = False) -> Optional[Any]:
        url = self.__prepare_url(path)
        headers = self.__get_headers()
        response = requests.get(url, params=params, headers=headers, timeout=self._timeout)

        if response.status_code == 404 and handle_404:
            self._log.warn(f"Status if 404 for request: GET {path}")
            return None

        response.raise_for_status()
        return response.json()

    def post_json(self, path, request_body: Any, params: dict | None = None) -> Optional[Any]:
        body_json_str = json_utils.to_json(request_body)
        response = requests.post(
            self.__prepare_url(path),
            params=params,
            json=body_json_str,
            headers=self.__get_headers(),
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def __prepare_url(self, path: str) -> str:
        _path = path
        if path.startswith("/"):
            _path = path[1:]
        return f"{self._base_url}/{_path}"

    def __get_access_token(self):
        return self._auth_func()

    def __get_headers(self):
        return {
            "x-okapi-token": self.__get_access_token(),
            "Content-Type": "application/json",
            "x-okapi-tenant": Env().get_tenant_id(),
        }
