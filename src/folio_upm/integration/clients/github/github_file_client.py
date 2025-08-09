import json
from typing import Any, Dict

import requests

from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class GithubFileClient:
    """Client for loading files from GitHub raw URLs."""

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)

    def load_object_safe(self, url: str) -> Dict[str, Any]:
        """
        Load JSON file from GitHub raw URL.

        Args:
            url: GitHub raw file URL

        Returns:
            Parsed JSON data or None if failed
        """
        try:
            response = requests.get(url, timeout=Env().get_http_client_timeout())
            response.raise_for_status()
            response_json = response.json()
            if not isinstance(response_json, dict):
                error_msg = "Invalid response type for URL expected dict (empty objects is used instead), got %s: %s"
                self._log.error(error_msg, type(response_json), url)
                return {}
            return response_json
        except (requests.RequestException, json.JSONDecodeError) as e:
            self._log.error("Error loading file (empty object will be used) from %s: %s", url, e)
            return {}
