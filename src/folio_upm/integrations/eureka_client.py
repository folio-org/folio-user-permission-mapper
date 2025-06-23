from collections import OrderedDict
from typing import List, Optional

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Capability, Role
from folio_upm.integrations.eureka_http_client import EurekaHttpClient
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.json_utils import JsonUtils
from folio_upm.utils.upm_env import Env


class EurekaClient(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("EurekaClient initialized.")
        self._client = EurekaHttpClient()

    def post_role(self, role: Role) -> Role:
        self._log.info(f"Creating role: name={role.name}, id={role.id}")

        role_body_str = JsonUtils.to_json(role.model_dump())
        response_json = self._client.post_json("/roles", role_body_str)
        return Role(**response_json)

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        self._log.debug(f"Retrieving role by name: {role_name}")

        query_params = {"query": f'name=="{role_name}"', "limit": 1, "offset": 0}
        response_json = self._client.get_json("/roles", params=query_params)
        roles = response_json.get("roles", [])

        if roles:
            self._log.debug(f"Role found by name: {role_name}")
            return Role(**JsonUtils.from_json(roles[0]))
        else:
            self._log.warning(f"Role not found by name: {role_name}")
            return None

    def post_role_users(self, role_id: str, users_ids: list[str]):
        self._log.info(f"Creating role-users assignments: roleId={role_id}, userIds={users_ids}")
        if not users_ids:
            self._log.warning(f"No users provided, skipping role-users assigment creation: roleId={role_id}")
            return []

        body = JsonUtils.to_json(OrderedDict({"roleId": role_id, "userIds": users_ids}))
        response = self._client.post_json("/roles/users", request_body=body)
        return response.get("userRoles", []) if response else []

    def post_role_capabilities(role_id: str, capabilities: List[str]):
        pass

    def post_role_capability_sets(role_id, capability_set_ids: List[str]):
        pass

    def get_capabilities_by_names(self, permission_names: list[str]) -> list[Capability]:
        self._log.info(f"Retrieving capabilities by permissions: {permission_names}")
        if not permission_names:
            self._log.warning("No permission names provided, skipping capability retrieval")
            return []
        query = CqlQueryUtils.any_match_by_field("permission", permission_names)
        response = self.__perform_get_request("/capabilities", params={"query": query, "limit": 100})
        return response.get("capabilities", []) if response else []

    def get_capability_sets_by_names(self, permission_names: list[str]) -> list[Capability]:
        self._log.info(f"Retrieving capability sets by permissions: {permission_names}")
        if not permission_names:
            self._log.warning("No permission names provided, skipping capability retrieval")
            return []
        query = CqlQueryUtils.any_match_by_field("permission", permission_names)
        response = self.__perform_get_request("/capability-sets", params={"query": query, "limit": 100})
        return response.get("capabilitySets", []) if response else []

    def load_resource_page(self, resource: str, limit: int, offset: int, query: str):
        """Load user permissions from Okapi."""
        self._log.info(f"Loading {resource} page: query='{query}', limit={limit}, offset={offset}")

        query_params = {"query": query, "limit": limit, "offset": offset}

        response = requests.get(
            url=f"{Env().get_okapi_url()}/{resource}",
            params=query_params,
        )

        if response.status_code == 200:
            entities = response.json().get(self.__to_camel_case(resource), [])
            self._log.info(f"Page loaded successfully: {len(entities)} permission(s) found.")
            return entities
        else:
            self._log.error(f"Failed to load '{resource}': {response.status_code} {response.text}")
            raise Exception(f"Failed to load '{resource}': {response.status_code} {response.text}")

    def __perform_get_request(self, path: str, params: dict = None):
        try:
            response = requests.get(
                f"{Env().get_eureka_url()}{path}",
                params=params,
            )
            if response.status_code == 200:
                return response.json()
            else:
                self._log.error(f"GET request failed: {response.status_code} {response.text}")
                return None
        except Exception as e:
            self._log.error(f"Exception during GET request: {e}")
            return None

    def __perform_post_request(self, path: str, json_body: str):
        try:
            response = requests.post(
                f"{Env().get_eureka_url()}{path}",
                json=json_body,
            )
            if response.status_code == 201:
                return response.json()
            elif response.status_code >= 400:
                self._log.warning(
                    f"Failed to perform POST request: path={path}, jsonBody='{json_body}', "
                    f"status={response.status_code}, error='{response.text}'"
                )
                return None
        except Exception as e:
            self._log.error(f"Failed to perform POST request: path={path}, jsonBody='{json_body}', error: {e}")
            return None

    @staticmethod
    def __to_camel_case(hyphen_case_str: str) -> str:
        s2 = hyphen_case_str.split("-")
        return s2[0] + "".join(word.capitalize() for word in s2[1:])
