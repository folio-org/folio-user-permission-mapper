from typing import List

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.migration import EntityMigrationResult
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.integration.services.role_capability_service import RoleCapabilityService
from folio_upm.integration.services.role_capability_set_service import RoleCapabilitySetService
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class RoleCapabilityFacade(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.info("RoleCapabilityServiceFacade initialized.")
        self._role_capability_service = RoleCapabilityService()
        self._role_capability_set_service = RoleCapabilitySetService()

    def assign_role_capabilities(self, role_capabilities: List[RoleCapabilitiesHolder]):
        migration_results = []
        for rch in role_capabilities:
            capability_sets, capabilities, issues = self.__find_by_permission_names(rch)
            migration_results += [self.__create_unmatched_result(rch, i) for i in issues]
            migration_results += self._role_capability_service.assign_to_role(rch, capabilities)
            migration_results += self._role_capability_set_service.assign_to_role(rch, capability_sets)
        return migration_results

    def __find_by_permission_names(self, rch: RoleCapabilitiesHolder):
        unmatched_ps_names = OrderedSet[str]([x.permissionName for x in rch.capabilities])
        capability_sets = self._role_capability_set_service.find_by_ps_names(unmatched_ps_names)
        unmatched_ps_names.remove_all([cs.permission for cs in capability_sets])

        capabilities = self._role_capability_service.find_by_ps_names(unmatched_ps_names)
        unmatched_ps_names.remove_all([c.permission for c in capabilities])
        unmatched_names = unmatched_ps_names.to_list()
        if unmatched_names:
            self._log.warning("Unmatched permission names found for role '%s': %s", rch.roleName, unmatched_names)
        return capability_sets, capabilities, unmatched_names

    @staticmethod
    def __create_unmatched_result(rch, permission_name):
        return EntityMigrationResult(
            status="not matched",
            entityName="role-capability(set)",
            entityId=f"Role: {rch.roleName} -> {rch.roleId}\nPS: {permission_name}",
            reason=f"Failed to find capability or capability set by PS name: {permission_name}",
        )
