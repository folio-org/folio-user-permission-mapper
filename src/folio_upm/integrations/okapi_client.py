from folio_upm.integrations.okapi_http_client import OkapiHttpClient
from folio_upm.utils import env, log_factory

_log = log_factory.get_logger(__name__)


class OkapiClient:

    def __init__(self):
        self._client = OkapiHttpClient()

    def read_module_descriptors(self):
        """Read Okapi modules from the Okapi server."""
        full = "true"
        _log.info(f"Reading Okapi module descriptors [full='{full}']...")

        path = f"/_/proxy/tenants/{env.get_tenant_id()}/modules"
        return self._client.get_json(path, params={"full": full})
