from typing import List, Tuple, override

import requests

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.eureka import CapabilitySet, Capability, RoleCapability
from folio_upm.dto.migration import HttpReqErr, EntityMigrationResult
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.integration.clients.eureka_client import EurekaClient
from folio_upm.integration.services.role_entity_service import RoleEntityService
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import CqlQueryUtils
from folio_upm.utils.loading_utils import PartitionedDataLoader
from folio_upm.utils.ordered_set import OrderedSet


class RoleCapabilityService(RoleEntityService, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__("capabilities")
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleService initialized.")

    @override
    def _load_entities_by_ps_names(self, query) -> List:
        return self._client.find_capabilities(query)

    @override
    def _get_result_entity_id(self, entity: RoleCapability):
        return entity.capabilityId

    @override
    def _assign_entities_to_role(self, role_id, capability_set_ids) -> List[RoleCapability]:
        return self._client.post_role_capabilities(role_id, capability_set_ids)

    @override
    def _create_success_result(self, role, entity_id) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_capability(role, entity_id, "success")

    @override
    def _create_skipped_result(self, role, entity_id) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_capability(role, entity_id, "skipped", "already exists")

    @override
    def _create_error_result(self, role, entity_id, error) -> EntityMigrationResult:
        return EntityMigrationResult.for_role_capability(role, entity_id, "error", "Failed to perform request", error)
