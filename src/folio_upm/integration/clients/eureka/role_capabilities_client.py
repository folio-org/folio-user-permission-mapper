from typing import List, override

from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.integration.clients.eureka.absract_role_entity_client import AbstractRoleEntityClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.role_capability import RoleCapability
from folio_upm.utils import log_factory


class RoleCapabilitiesClient(AbstractRoleEntityClient[RoleCapability], metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("UserCapabilitiesClient initialized.")
        self._http_client = EurekaHttpClient()

    @override
    def find_by_query(self, query: str, limit: int, offset: int) -> List[RoleCapability]:
        query_params = {"query": query, "limit": limit, "offset": offset}
        response = self._http_client.get_json("/roles/capabilities", params=query_params)
        return [RoleCapability(**rc) for rc in response.get("roleCapabilities", [])]

    @override
    def create_role_entity(self, role_id: str, entity_ids: List[str]) -> List[RoleCapability]:
        body = {"roleId": role_id, "capabilityIds": entity_ids}
        response = self._http_client.post_json("/roles/capabilities", request_body=body)
        role_capabilities_json = response.get("roleCapabilities", []) if response else []
        return [RoleCapability(**rc) for rc in role_capabilities_json]

    @override
    def update_role_entity(self, role_id: str, entity_ids: List[str]) -> None:
        body = {"capabilityIds": entity_ids}
        self._http_client.put_json(f"/roles/{role_id}/capabilities", request_body=body)

    @override
    def get_target_entity_id(self, entity: RoleCapability) -> str:
        return entity.capabilityId
