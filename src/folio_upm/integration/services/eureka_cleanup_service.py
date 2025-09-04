from typing import List

from folio_upm.integration.services.role_capability_facade import RoleCapabilityFacade
from folio_upm.integration.services.role_service import RoleService
from folio_upm.model.cleanup.hash_role_cleanup_record import HashRoleCleanupRecord
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.report.hash_roles_cleanup_report import HashRolesCleanupReport
from folio_upm.utils import log_factory


class EurekaCleanupService(metaclass=SingletonMeta):

    def __init__(self, hash_role_cleanup_records: List[HashRoleCleanupRecord]):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._hash_role_cleanup_records = hash_role_cleanup_records
        self._role_service = RoleService()
        self._role_capability_facade = RoleCapabilityFacade()

    def perform_cleanup(self) -> HashRolesCleanupReport:
        self._log.info("Starting Eureka Hash-Roles cleanup process...")
        records = self._hash_role_cleanup_records
        role_capabilities_rs = self._role_capability_facade.update_role_capabilities(records)
        removed_roles_rs = self._role_service.delete_roles(records)
        self._log.info("Eureka Hash-Roles cleanup process completed successfully.")
        return HashRolesCleanupReport(roles=removed_roles_rs, roleCapabilities=role_capabilities_rs)
