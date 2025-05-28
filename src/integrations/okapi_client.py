import requests

from utils import env, log_factory
from services import login_service

_log = log_factory.get_logger(__name__)


def read_module_descriptors():
    """Read Okapi modules from the Okapi server."""
    full = 'true'
    _log.info(f"Reading Okapi module descriptors [full='{full}']...")
    _headers = {
        'Content-Type': 'application/json',
        'X-Okapi-Token': login_service.get_admin_token()
    }

    _queryParameters = {'full': full}

    response = requests.get(
        url=f"{env.get_okapi_url()}/_/proxy/tenants/{env.get_tenant_id()}/modules",
        headers=_headers, params=_queryParameters)

    if response.status_code == 200:
        return response.json()
    else:
        _log.error(f"Failed to load Okapi modules: {response.status_code} {response.text}")
        raise Exception(f"Failed to load Okapi modules: {response.status_code} {response.text}")
