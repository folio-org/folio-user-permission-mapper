import requests

from services import login_service
from utils import env, log_factory

_log = log_factory.get_logger(__name__)


def load_perms_page(limit, offset, query, expanded=False):
    """Load user permissions from Okapi."""
    tenant_id = env.get_tenant_id()
    _log.info("Loading permissions page: "
              f"query='{query}', limit={limit}, tenantId={tenant_id}, offset={offset}, ")

    headers = {
        'Content-Type': 'application/json',
        'X-Okapi-Tenant': tenant_id,
        'X-Okapi-Token': login_service.get_admin_token()
    }

    query_params = {
        'query': query,
        'limit': limit,
        "offset": offset,
        'expanded': str(expanded).lower(),
    }

    response = requests.get(
        url=f"{env.get_okapi_url()}/perms/permissions",
        params=query_params, headers=headers)

    if response.status_code == 200:
        permissions = response.json().get('permissions', [])
        _log.info(f"Page loaded successfully: {len(permissions)} permission(s) found.")
        return permissions
    else:
        _log.error(f"Failed to load user permissions: {response.status_code} {response.text}")
        raise Exception(f"Failed to load user permissions: {response.status_code} {response.text}")


def load_user_permissions_by_id(ids):
    """Load user permissions from Okapi."""
    tenant_id = env.get_tenant_id()
    query = f'id==({" or ".join(map(lambda x: f'"{x}"', ids))})'
    _log.info(f"Loading permissions page: tenantId={tenant_id}, ids={len(ids)}, query='{query}'")

    headers = {
        'Content-Type': 'application/json',
        'X-Okapi-Tenant': tenant_id,
        'X-Okapi-Token': login_service.get_admin_token()
    }

    query_parameters = {'query': query, 'limit': 500, }

    response = requests.get(
        url=f"{env.get_okapi_url()}/perms/users",
        params=query_parameters, headers=headers)

    if response.status_code == 200:
        permissionUsers = response.json()['permissionUsers']
        _log.info(f"Page loaded successfully: {len(permissionUsers)} permissionUser(s) found.")
        return permissionUsers
    else:
        _log.error(f"Failed to load user permissions: {response.status_code} {response.text}")
        raise Exception(f"Failed to load user permissions: {response.status_code} {response.text}")
