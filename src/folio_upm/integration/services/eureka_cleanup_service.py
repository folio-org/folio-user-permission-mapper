from typing import List

from folio_upm.dto.cleanup import HashRoleCleanupData
from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.results import EurekaCleanUpResult
from folio_upm.integration.services.role_capability_facade import RoleCapabilityFacade
from folio_upm.integration.services.role_service import RoleService
from folio_upm.utils import log_factory


class EurekaCleanupService(metaclass=SingletonMeta):

    def __init__(self, clean_hash_roles: List[HashRoleCleanupData]):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._clean_hash_roles = clean_hash_roles
        self._role_service = RoleService()
        self._role_capability_facade = RoleCapabilityFacade()

    def perform_cleanup(self) -> EurekaCleanUpResult:
        self._log.info("Starting Eureka Hash-Roles cleanup process...")
        role_capabilities_rs = self._role_capability_facade.update_role_capabilities(self._clean_hash_roles)
        removed_roles_rs = self._role_service.delete_roles(self._clean_hash_roles)
        self._log.info("Eureka Hash-Roles cleanup process completed successfully.")
        return EurekaCleanUpResult(roles=removed_roles_rs, roleCapabilities=role_capabilities_rs)
