from collections import OrderedDict
from typing import List

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import Capability, Role, RoleCapability, RoleCapabilitySet, CapabilitySet, UserRoles
from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.utils import log_factory


class EurekaClient(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("EurekaClient initialized.")
        self._client = EurekaHttpClient()

    def post_role(self, role: Role) -> Role:
        response_json = self._client.post_json("/roles", role.model_dump())
        return Role(**response_json)

    def post_role_users(self, role_id: str, users_ids: list[str]) -> List[UserRoles]:
        body = OrderedDict({"roleId": role_id, "userIds": users_ids})
        response = self._client.post_json("/roles/users", request_body=body)
        user_roles = response.get("userRoles", []) if response else []
        return [UserRoles(**ur) for ur in user_roles]

    def post_role_capabilities(self, role_id: str, capability_ids: List[str]):
        body = OrderedDict({"roleId": role_id, "capabilityIds": capability_ids})
        response = self._client.post_json("/roles/capabilities", request_body=body)
        role_capabilities_json = response.get("roleCapabilities", []) if response else []
        return [RoleCapability(**rc) for rc in role_capabilities_json]

    def post_role_capability_sets(self, role_id, capability_set_ids: List[str]):
        body = OrderedDict({"roleId": role_id, "capabilitySetIds": capability_set_ids})
        response = self._client.post_json("/roles/capability-sets", request_body=body)
        role_capability_sets_json = response.get("roleCapabilitySets", []) if response else []
        return [RoleCapabilitySet(**rc) for rc in role_capability_sets_json]

    def find_roles_by_query(self, cql_query: str) -> List[Role]:
        self._log.debug("Retrieving roles by query: query=%s", cql_query)
        response = self._client.get_json("/roles", params={"query": cql_query, "limit": 500})
        return [Role(**role_dict) for role_dict in response.get("roles", [])]

    def find_capabilities(self, cql_query: str) -> list[Capability]:
        response = self._client.get_json("/capabilities", params={"query": cql_query, "limit": 500})
        found_capabilities = response.get("capabilities", []) if response else []
        return [Capability(**c) for c in found_capabilities]

    def find_capability_sets(self, cql_query: str) -> list[CapabilitySet]:
        response = self._client.get_json("/capability-sets", params={"query": cql_query, "limit": 500})
        found_capability_sets = response.get("capabilitySets", []) if response else []
        return [CapabilitySet(**cs) for cs in found_capability_sets]

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
