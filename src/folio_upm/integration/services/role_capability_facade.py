from typing import List, Tuple

from folio_upm.integration.services.role_capability_service import RoleCapabilityService
from folio_upm.integration.services.role_capability_set_service import RoleCapabilitySetService
from folio_upm.integration.services.role_service import RoleService
from folio_upm.model.analysis.analyzed_role_capabilities import AnalyzedRoleCapabilities
from folio_upm.model.cleanup.hash_role_cleanup_record import HashRoleCleanupRecord
from folio_upm.model.cls_support import SingletonMeta
from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.report.http_request_result import HttpRequestResult
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet


class RoleCapabilityFacade(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleCapabilityServiceFacade initialized.")
        self._role_service = RoleService()
        self._rc_service = RoleCapabilityService()
        self._rcs_service = RoleCapabilitySetService()

    def assign_role_capabilities(self, role_capabilities: List[AnalyzedRoleCapabilities]) -> List[HttpRequestResult]:
        migration_results = list[HttpRequestResult]()
        role_capabilities_counter = 1
        total_role_capabilities = len(role_capabilities)
        self._log.info("Total role capabilities to assign: %s", total_role_capabilities)
        for rch in role_capabilities:
            role_name = rch.roleName
            role_by_name = self._role_service.find_role_by_name(role_name)
            if role_by_name is None:
                self._log.warning("Role '%s' not found by name, skipping capability assignment...", role_name)
                migration_results.append(HttpRequestResult.role_capability_not_found_result(role_name))
                continue
            capability_sets, capabilities, issues = self.__find_by_permission_names(rch)
            migration_results += [self.__create_unmatched_result(role_by_name, i) for i in issues]
            role_capability_assign_rs = self._rc_service.assign_to_role(role_by_name, capabilities)
            role_set_assign_rs = self._rcs_service.assign_to_role(role_by_name, capability_sets)
            migration_results += role_capability_assign_rs
            migration_results += role_set_assign_rs
            self._log.info("Role capabilities processed: %s/%s", role_capabilities_counter, total_role_capabilities)
            role_capabilities_counter += 1

        self._log.info("Role capabilities assigned: %s", total_role_capabilities)
        return migration_results

    def update_role_capabilities(self, cleanup_records: List[HashRoleCleanupRecord]) -> List[HttpRequestResult]:
        cleanup_result = list[HttpRequestResult]()
        total_records = len(cleanup_records)
        records_counter = 1
        self._log.info("Total cleanup records: %s", total_records)
        for hr in cleanup_records:
            cleanup_result += self._rc_service.update(hr.role, hr.capabilities)
            cleanup_result += self._rcs_service.update(hr.role, hr.capabilitySets)
            self._log.info("Role cleanup processed: %s/%s", records_counter, total_records)
            records_counter += 1
        self._log.info("Role capabilities updated: %s", records_counter)
        return cleanup_result

    def __find_by_permission_names(
        self, arc: AnalyzedRoleCapabilities
    ) -> Tuple[List[CapabilitySet], List[Capability], List[str]]:
        unmatched_ps_names = OrderedSet[str]([x.permissionName for x in arc.capabilities])
        capability_sets = self._rcs_service.find_by_ps_names(unmatched_ps_names.to_list())
        unmatched_ps_names.remove_all([cs.permission for cs in capability_sets])

        capabilities = self._rc_service.find_by_ps_names(unmatched_ps_names.to_list())
        unmatched_ps_names.remove_all([c.permission for c in capabilities])
        unmatched_names = unmatched_ps_names.to_list()
        if unmatched_names:
            self._log.warning("Unmatched permission names found for role '%s': %s", arc.roleName, unmatched_names)
        return capability_sets, capabilities, unmatched_names

    @staticmethod
    def __create_unmatched_result(role, permission_name) -> HttpRequestResult:
        return HttpRequestResult(
            status="not_matched",
            srcEntityName="role",
            srcEntityId=role.id,
            tarEntityName="capability | capability-set",
            tarEntityId=permission_name,
            reason="Failed to find capability or capability set by name",
        )
