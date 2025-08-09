from typing import List

from typing_extensions import override

from folio_upm.integration.clients.base.eureka_http_client import EurekaHttpClient
from folio_upm.integration.clients.eureka.absract_role_entity_client import AbstractRoleEntityClient
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.role_capability_set import RoleCapabilitySet
from folio_upm.utils import log_factory


class RoleCapabilitySetClient(AbstractRoleEntityClient[RoleCapabilitySet], metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleCapabilitySetClient initialized.")
        self._http_client = EurekaHttpClient()

    @override
    def find_by_query(self, query: str, limit: int, offset: int) -> List[RoleCapabilitySet]:
        query_params = {"query": query, "limit": limit, "offset": offset}
        response = self._http_client.get_json("/roles/capabilities", params=query_params)
        if not isinstance(response, dict):
            error_msg_template = "Invalid response type for role-capability-sets query(%s, %s, %s): %s"
            self._log.error(error_msg_template, query, limit, offset, str(response))
            return []
        return [RoleCapabilitySet(**rc) for rc in response.get("roleCapabilitySets", [])]

    @override
    def create_role_entity(self, role_id: str, entity_ids: List[str]) -> List[RoleCapabilitySet]:
        body = {"roleId": role_id, "capabilitySetIds": entity_ids}
        response = self._http_client.post_json("/roles/capability-sets", request_body=body)
        if not isinstance(response, dict):
            error_msg_template = "Invalid response type for role-capability-sets creation (%s, %s): %s"
            self._log.error(error_msg_template, role_id, entity_ids, str(response))
            return []
        role_capability_sets_json = response.get("roleCapabilitySets", []) if response else []
        return [RoleCapabilitySet(**rc) for rc in role_capability_sets_json]

    @override
    def update_role_entity(self, role_id: str, entity_ids: List[str]) -> None:
        body = {"capabilitySetIds": entity_ids}
        self._http_client.put_json(f"/roles/{role_id}/capability-sets", request_body=body)

    @override
    def get_target_entity_id(self, entity: RoleCapabilitySet) -> str:
        return entity.capabilitySetId
