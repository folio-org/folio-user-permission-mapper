import requests

from folio_upm.services import login_service
from folio_upm.utils import common_utils, env, log_factory

_log = log_factory.get_logger(__name__)


def load_perms_page(limit, offset, query, expanded=False):
    """Load user permissions from Okapi."""
    _log.info(f"Loading permissions page: query='{query}', limit={limit}, offset={offset}")

    query_params = {
        "query": query,
        "limit": limit,
        "offset": offset,
        "expanded": str(expanded).lower(),
    }

    response = requests.get(
        url=f"{env.get_okapi_url()}/perms/permissions",
        params=query_params,
        headers=(__get_okapi_headers()),
    )

    if response.status_code == 200:
        permissions = response.json().get("permissions", [])
        _log.info(f"Page loaded successfully: {len(permissions)} permission(s) found.")
        return permissions
    else:
        _log.error(f"Failed to load user permissions: {response.status_code} {response.text}")
        raise Exception(f"Failed to load user permissions: {response.status_code} {response.text}")


def load_user_permissions_by_id(ids):
    """Load user permissions from Okapi."""
    query = common_utils.any_match_by_field_cql("id", ids)
    _log.info(f"Loading permissions page: query='{query}'")

    response = requests.get(
        url=f"{env.get_okapi_url()}/perms/users",
        params={
            "query": query,
            "limit": 500,
        },
        headers=(__get_okapi_headers()),
    )

    if response.status_code == 200:
        permissionUsers = response.json()["permissionUsers"]
        _log.info(f"Page loaded successfully: {len(permissionUsers)} permissionUser(s) found.")
        return permissionUsers
    else:
        _log.error(f"Failed to load user permissions: {response.status_code} {response.text}")
        raise Exception(f"Failed to load user permissions: {response.status_code} {response.text}")


def __get_okapi_headers():
    return {
        "Content-Type": "application/json",
        "X-Okapi-Tenant": env.get_tenant_id(),
        "X-Okapi-Token": login_service.get_okapi_token(),
    }
