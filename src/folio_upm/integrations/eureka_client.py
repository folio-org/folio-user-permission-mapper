from collections import OrderedDict
from typing import List, Optional

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Role, Capability
from folio_upm.integrations.eureka_http_client import EurekaHttpClient
from folio_upm.utils import env, json_utils, log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.json_utils import from_json

_log = log_factory.get_logger(__name__)


class EurekaClient(metaclass=SingletonMeta):
    """Singleton class to interact with the Eureka service."""

    def __init__(self):
        _log.info("EurekaClient initialized.")
        self._client = EurekaHttpClient()

    def post_role(self, role: Role) -> Role:
        _log.info(f"Creating role: name={role.name}, id={role.id}")

        role_body_str = json_utils.to_json(role.model_dump())
        response_json = self._client.post_json("/roles", role_body_str)
        return Role(**response_json)

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        _log.debug(f"Retrieving role by name: {role_name}")

        query_params = {"query": f'name=="{role_name}"', "limit": 1, "offset": 0}
        response_json = self._client.get_json("/roles", params=query_params)
        roles = response_json.get("roles", [])

        if roles:
            _log.debug(f"Role found by name: {role_name}")
            return Role(**from_json(roles[0]))
        else:
            _log.warning(f"Role not found by name: {role_name}")
            return None

    def post_role_users(self, role_id: str, users_ids: list[str]):
        _log.info(f"Creating role-users assignments: roleId={role_id}, userIds={users_ids}")
        if not users_ids:
            _log.warning(f"No users provided, skipping role-users assigment creation: roleId={role_id}")
            return []

        body = json_utils.to_json(OrderedDict({"roleId": role_id, "userIds": users_ids}))
        response = self._client.post_json("/roles/users", request_body=body)
        return response.get("userRoles", []) if response else []

    def post_role_capabilities(role_id: str, capabilities: List[str]):
        pass

    def post_role_capability_sets(role_id, capability_set_ids: List[str]):
        pass

    def get_capabilities_by_names(self, permission_names: list[str]) -> list[Capability]:
        _log.info(f"Retrieving capabilities by permissions: {permission_names}")
        if not permission_names:
            _log.warning("No permission names provided, skipping capability retrieval")
            return []
        query = CqlQueryUtils.any_match_by_field("permission", permission_names)
        response = self.__perform_get_request("/capabilities", params={"query": query, "limit": 100})
        return response.get("capabilities", []) if response else []

    def get_capability_sets_by_names(self, permission_names: list[str]) -> list[Capability]:
        _log.info(f"Retrieving capability sets by permissions: {permission_names}")
        if not permission_names:
            _log.warning("No permission names provided, skipping capability retrieval")
            return []
        query = CqlQueryUtils.any_match_by_field("permission", permission_names)
        response = self.__perform_get_request("/capability-sets", params={"query": query, "limit": 100})
        return response.get("capabilitySets", []) if response else []

    def load_resource_page(self, resource: str, limit: int, offset: int, query: str):
        """Load user permissions from Okapi."""
        _log.info(f"Loading {resource} page: query='{query}', limit={limit}, offset={offset}")

        query_params = {"query": query, "limit": limit, "offset": offset}

        response = requests.get(
            url=f"{env.get_okapi_url()}/{resource}",
            params=query_params,
            headers=(self.__get_eureka_headers()),
        )

        if response.status_code == 200:
            entities = response.json().get(self.__to_camel_case(resource), [])
            _log.info(f"Page loaded successfully: {len(entities)} permission(s) found.")
            return entities
        else:
            _log.error(f"Failed to load '{resource}': {response.status_code} {response.text}")
            raise Exception(f"Failed to load '{resource}': {response.status_code} {response.text}")

    def __perform_get_request(self, path: str, params: dict = None):
        try:
            response = requests.get(
                f"{env.get_eureka_url()}{path}",
                headers=self.__get_eureka_headers(),
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

    def __perform_post_request(self, path: str, json_body: str):
        try:
            response = requests.post(
                f"{env.get_eureka_url()}{path}",
                headers=self.__get_eureka_headers(),
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

    def __get_eureka_headers(self):
        return {
            "Authorization": f"Bearer {self._login_service.get_eureka_token()}",
            "x-okapi-tenant": env.get_tenant_id(),
            "Content-Type": "application/json",
        }

    @staticmethod
    def __to_camel_case(hyphen_case_str: str) -> str:
        s2 = hyphen_case_str.split("-")
        return s2[0] + "".join(word.capitalize() for word in s2[1:])
