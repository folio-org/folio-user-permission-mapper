from typing import List

from folio_upm.dto.cls_support import SingletonMeta
from folio_upm.dto.migration import EntityMigrationResult
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.integration.services.role_capability_service import RoleCapabilityService
from folio_upm.integration.services.role_capability_set_service import RoleCapabilitySetService
from folio_upm.integration.services.role_service import RoleService
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class RoleCapabilityFacade(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleCapabilityServiceFacade initialized.")
        self._role_capability_service = RoleCapabilityService()
        self._role_service = RoleService()
        self._role_capability_set_service = RoleCapabilitySetService()

    def assign_role_capabilities(self, role_capabilities: List[RoleCapabilitiesHolder]):
        migration_results = []
        for rch in role_capabilities:
            role_name = rch.roleName
            role_by_name = self._role_service.find_role_by_name(role_name)
            if role_by_name is None:
                self._log.warning("Role '%s' not found by name, skipping capability assignment...", role_name)
                migration_results.append(EntityMigrationResult.role_not_found_result(role_name))
                continue
            capability_sets, capabilities, issues = self.__find_by_permission_names(rch)
            migration_results += [self.__create_unmatched_result(role_by_name, i) for i in issues]
            role_capability_assign_rs = self._role_capability_service.assign_to_role(role_by_name, capabilities)
            role_set_assign_rs = self._role_capability_set_service.assign_to_role(role_by_name, capability_sets)
            migration_results += role_capability_assign_rs
            migration_results += role_set_assign_rs
        return migration_results

    def __find_by_permission_names(self, rch: RoleCapabilitiesHolder):
        unmatched_ps_names = OrderedSet[str]([x.permissionName for x in rch.capabilities])
        capability_sets = self._role_capability_set_service.find_by_ps_names(unmatched_ps_names.to_list())
        unmatched_ps_names.remove_all([cs.permission for cs in capability_sets])

        capabilities = self._role_capability_service.find_by_ps_names(unmatched_ps_names.to_list())
        unmatched_ps_names.remove_all([c.permission for c in capabilities])
        unmatched_names = unmatched_ps_names.to_list()
        if unmatched_names:
            self._log.warning("Unmatched permission names found for role '%s': %s", rch.roleName, unmatched_names)
        return capability_sets, capabilities, unmatched_names

    @staticmethod
    def __create_unmatched_result(role, permission_name):
        return EntityMigrationResult(
            status="not_matched",
            entityName="capability or capability-set",
            entityId=f"Role: {role.name} -> {role.id}\nPS: {permission_name}",
            reason=f"Failed to find capability or capability set by PS name: {permission_name}",
        )
