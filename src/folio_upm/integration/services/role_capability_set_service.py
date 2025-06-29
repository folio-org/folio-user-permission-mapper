from typing import List, override

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import RoleCapabilitySet
from folio_upm.dto.migration import EntityMigrationResult
from folio_upm.integration.services.role_entity_service import RoleEntityService
from folio_upm.utils import log_factory


class RoleCapabilitySetService(RoleEntityService, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__("capability-sets")
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleService initialized.")

    @override
    def _load_entities_by_ps_names(self, query) -> List:
        return self._client.find_capability_sets(query)

    @override
    def _get_result_entity_id(self, entity: RoleCapabilitySet) -> str:
        return entity.capabilitySetId

    @override
    def _assign_entities_to_role(self, role_id, capability_set_ids) -> List[RoleCapabilitySet]:
        return self._client.post_role_capability_sets(role_id, capability_set_ids)

    @override
    def _create_success_result(self, role, entity_id) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_capability_set(role, entity_id, "success")

    @override
    def _create_skipped_result(self, role, entity_id) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_capability_set(role, entity_id, "skipped", "already exists")

    @override
    def _create_error_result(self, role, entity_id, error) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_capability_set(
            role, entity_id, "error", "Failed to perform request", error
        )
