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
        response_json = self._client.post_json("/roles", role.model_dump())
        return Role(**response_json)

    def find_roles_by_query(self, role_names_query) -> List[Role]:
        self._log.debug("Retrieving roles by query: query=%s", role_names_query)
        response = self._client.get_json("/roles", role_names_query)
        return [Role(**role_dict) for role_dict in response.get("roles", [])]

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

    def load_page(self, resource: str, path: str, query: str, limit: int, offset: int):
        query_params = {"query": query, "limit": limit, "offset": offset}
        response_json = self._client.get_json(path, params=query_params)
        return response_json.get(resource, [])
