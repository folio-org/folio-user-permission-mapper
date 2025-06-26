from collections import OrderedDict
from typing import List, Optional

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Capability, Role, RoleCapability, RoleCapabilitySet
from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.utils import log_factory
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

    def find_roles_by_query(self, role_names_query) -> List[Role]:
        response = self._client.get_json("/roles", role_names_query)
        return [Role(**role_dict) for role_dict in response.get("roles", [])]

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

    def post_role_capabilities(self, role_id: str, capability_ids: List[str]):
        body = OrderedDict({"roleId": role_id, "capabilitySetIds": capability_ids})
        response = self._client.post_json("/roles/capabilities", request_body=body)
        return response.get("roleCapabilities", []) if response else []

    def post_role_capability_sets(self, role_id, capability_set_ids: List[str]):
        body = OrderedDict({"roleId": role_id, "capabilitySetIds": capability_set_ids})
        response = self._client.post_json("/roles/capability-sets", request_body=body)
        return response.get("roleCapabilitySets", []) if response else []

    def find_capabilities(self, cql_query: str) -> list[Capability]:
        response = self._client.get_json("/capabilities", params={"query": cql_query, "limit": 100})
        return response.get("capabilities", []) if response else []

    def find_capability_sets(self, cql_query: str) -> list[Capability]:
        response = self._client.get_json("/capability-sets", params={"query": cql_query, "limit": 100})
        return response.get("capabilities", []) if response else []

    def find_role_capabilities(self, query: str, limit: int, offset: int) -> List[RoleCapability]:
        query_params = {"query": query, "limit": limit, "offset": offset}
        response = self._client.get_json("/roles/capabilities", params=query_params)
        return [RoleCapability(**rc) for rc in response.get("roleCapabilities", [])]

    def find_role_capability_sets(self, query: str, limit: int, offset: int) -> List[RoleCapabilitySet]:
        query_params = {"query": query, "limit": limit, "offset": offset}
        response = self._client.get_json("/roles/capabilities", params=query_params)
        return [RoleCapabilitySet(**rc) for rc in response.get("roleCapabilitySets", [])]

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
