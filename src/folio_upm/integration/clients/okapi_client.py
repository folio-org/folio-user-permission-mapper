from folio_upm.integration.clients.base.okapi_http_client import OkapiHttpClient
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class OkapiClient:

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("OkapiClient initialized.")
        self._client = OkapiHttpClient()

    def read_module_descriptors(self):
        """Read Okapi modules from the Okapi server."""
        full = "true"
        self._log.info(f"Reading Okapi module descriptors [full='{full}']...")

        path = f"/_/proxy/tenants/{Env().get_tenant_id()}/modules"
        return self._client.get_json(path, params={"full": full})
