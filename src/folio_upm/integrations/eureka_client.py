from collections import OrderedDict
from typing import List, Optional

import requests

from folio_upm.dto.models import Capability, Role
from folio_upm.services import login_service
from folio_upm.utils import common_utils, env, json_utils, log_factory
from folio_upm.utils.json_utils import from_json

_log = log_factory.get_logger(__name__)


def post_role(role: Role) -> Optional[Role]:
    _log.info(f"Creating role: name={role.name}, id={role.id}")
    role_name = role.name.strip()
    if not role_name:
        _log.error("Role name cannot be empty, skipping role creation")
        return None

    role_to_create = Role(id=role.id, name=role_name, description=role.description)
    role_body_str = json_utils.to_json(role_to_create.model_dump())
    try:
        response = requests.post(
            env.get_eureka_url() + "/roles",
            headers=__get_eureka_headers(),
            json=role_body_str,
        )
        if response.status_code == 201:
            _log.info(f"Role {role_name} created")
            return Role(**from_json(response.json()))
        elif response.status_code == 409:
            _log.warning(f"Role {role_name} already exists")
            return get_role_by_name(role_name)
    except Exception as e:
        _log.error(f"Failed to create role {role_name}: {e}")
        return None


def get_role_by_name(role_name: str) -> Optional[Role]:
    _log.info(f"Retrieving role by name: {role_name}")
    try:
        response = requests.get(
            env.get_eureka_url() + "/roles",
            params={"query": f'name=="{role_name}"', "limit": 1, "offset": 0},
            headers=__get_eureka_headers(),
        )
        if response.status_code == 200:
            roles = response.json().get("roles", [])
            if roles:
                _log.debug(f"Role found by name: {role_name}")
                return Role(**from_json(roles[0]))
            else:
                _log.warning(f"Role not found by name: {role_name}")
                return None
    except Exception as e:
        _log.error(f"Failed to retrieve role by name {role_name}: {e}")
        return None


def post_role_users(role_id: str, users_ids: list[str]):
    _log.info(f"Creating role-users assignments: roleId={role_id}, userIds={users_ids}")
    if not users_ids:
        _log.warning(f"No users provided, skipping role-users assigment creation: roleId={role_id}")
        return []

    body = json_utils.to_json(OrderedDict({"roleId": role_id, "userIds": users_ids}))
    response = __perform_post_request("/roles/users", body)
    return response.get("userRoles", []) if response else []


def post_role_capabilities(role_id: str, capabilities: List[str]) -> Optional:
    pass


def post_role_capability_sets(role_id, capability_set_ids: List[str]):
    pass


def get_capabilities_by_names(permission_names: list[str]) -> list[Capability]:
    _log.info(f"Retrieving capabilities by permissions: {permission_names}")
    if not permission_names:
        _log.warning("No permission names provided, skipping capability retrieval")
        return []
    query = common_utils.any_match_by_field_cql("permission", permission_names)
    response = __perform_get_request("/capabilities", params={"query": query, "limit": 100})
    return response.get("capabilities", []) if response else []


def get_capability_sets_by_names(permission_names: list[str]) -> list[Capability]:
    _log.info(f"Retrieving capability sets by permissions: {permission_names}")
    if not permission_names:
        _log.warning("No permission names provided, skipping capability retrieval")
        return []
    query = common_utils.any_match_by_field_cql("permission", permission_names)
    response = __perform_get_request("/capability-sets", params={"query": query, "limit": 100})
    return response.get("capabilitySets", []) if response else []


def __perform_get_request(path: str, params: dict = None):
    try:
        response = requests.get(
            f"{env.get_eureka_url()}{path}",
            headers=__get_eureka_headers(),
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        else:
            _log.error(f"GET request failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        _log.error(f"Exception during GET request: {e}")
        return None


def __perform_post_request(path: str, json_body: str):
    try:
        response = requests.post(
            f"{env.get_eureka_url()}{path}",
            headers=__get_eureka_headers(),
            json=json_body,
        )
        if response.status_code == 201:
            return response.json()
        elif response.status_code >= 400:
            _log.warning(
                f"Failed to perform POST request: path={path}, jsonBody='{json_body}', "
                f"status={response.status_code}, error='{response.text}'"
            )
            return None
    except Exception as e:
        _log.error(f"Failed to perform POST request: path={path}, jsonBody='{json_body}', error: {e}")
        return None


def __get_eureka_headers():
    return {
        "Authorization": f"Bearer {login_service.get_eureka_token()}",
        "x-okapi-tenant": env.get_tenant_id(),
        "Content-Type": "application/json",
    }
