from typing import Dict, List

from folio_upm.integration.clients.base.okapi_http_client import OkapiHttpClient
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class OkapiClient:

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("OkapiClient initialized.")
        self._client = OkapiHttpClient()

    def read_module_descriptors(self) -> List[Dict]:
        """Read Okapi modules from the Okapi server."""
        full = "true"
        self._log.info(f"Reading Okapi module descriptors [full='{full}']...")

        path = f"/_/proxy/tenants/{Env().get_tenant_id()}/modules"
        response_json = self._client.get_json(path, params={"full": full})
        if not isinstance(response_json, list):
            error_msg_template = "Invalid response type for okapi module permissions query"
            self._log.error(error_msg_template)
            return []
        return response_json
