from typing import Callable, List, Tuple

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
from folio_upm.utils.cql import CQL
from folio_upm.utils.iterable_utils import IterableUtils
from folio_upm.utils.ordered_set import OrderedSet


class RoleCapabilityFacade(metaclass=SingletonMeta):

    def __init__(self):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("RoleCapabilityServiceFacade initialized.")
        self._role_service = RoleService()
        self._rc_service = RoleCapabilityService()
        self._rcs_service = RoleCapabilitySetService()

    def assign_role_entities(self, arc_list: List[AnalyzedRoleCapabilities]) -> List[HttpRequestResult]:
        migration_results = list[HttpRequestResult]()
        role_capabilities_counter = 1
        total_role_capabilities = len(arc_list)
        self._log.info("Total role capabilities to assign: %s", total_role_capabilities)
        for analyzed_role_capabilities in arc_list:
            role_name = analyzed_role_capabilities.roleName
            role_by_name = self._role_service.find_role_by_name(role_name)
            if role_by_name is None:
                self._log.warning("Role '%s' not found by name, skipping capability assignment...", role_name)
                migration_results.append(HttpRequestResult.role_capability_not_found_result(role_name))
                continue
            capability_sets, capabilities, issues = self.__find_role_entities(analyzed_role_capabilities)
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
        self._log.info("Number of cleanup records: %s", total_records)

        record_counter = 0
        for hr in cleanup_records:
            cleanup_result += self._rcs_service.update(hr.role, hr.capabilitySets)
            record_counter += 1
            self._log.info("Role-capability-sets processed: %s/%s", record_counter, total_records)
        self._log.info("Role-capability-sets updated: %s", record_counter)

        record_counter = 0
        for hr in cleanup_records:
            cleanup_result += self._rc_service.update(hr.role, hr.capabilities)
            record_counter += 1
            self._log.info("Role-capabilities processed: %s/%s", record_counter, total_records)
        self._log.info("Role-capabilities updated: %s", record_counter)

        return cleanup_result

    def __find_role_entities(
        self, arc: AnalyzedRoleCapabilities
    ) -> Tuple[List[CapabilitySet], List[Capability], List[str]]:
        found_capability_sets = list[CapabilitySet]()
        found_capabilities = list[Capability]()
        unmatched_values = list[str]()
        if not arc.capabilities:
            return found_capability_sets, found_capabilities, unmatched_values

        # gather capabilities by permission name
        ps_names = [x.permissionName for x in arc.capabilities if x.permissionName]
        entities_by_ps_name = self.__find_by(ps_names, CQL.any_match_by_permission, lambda x: x.permission)
        found_capabilities += entities_by_ps_name[1]
        found_capability_sets += entities_by_ps_name[0]
        unmatched_values += entities_by_ps_name[2]

        # gather extra capabilities by name (if eureka load result was not provided)
        capability_names = [x.name for x in arc.capabilities if not x.permissionName and x.name]
        entities_by_name = self.__find_by(capability_names, CQL.any_match_by_name, lambda x: x.name)
        found_capabilities += entities_by_name[1]
        found_capability_sets += entities_by_name[0]
        unmatched_values += entities_by_name[2]
        unmatched_values = IterableUtils.unique_values(entities_by_name[2])

        if unmatched_values:
            self._log.warning("Unmatched entities found for role '%s': %s", arc.roleName, unmatched_values)

        return (
            IterableUtils.unique_values_by_key(found_capability_sets, lambda x: x.id),
            IterableUtils.unique_values_by_key(found_capabilities, lambda x: x.id),
            unmatched_values,
        )

    def __find_by(
        self,
        identifiers: List[str],
        query_builder_func: Callable[[List[str]], str],
        value_accessor: Callable[[Capability | CapabilitySet], str],
    ) -> Tuple[List[CapabilitySet], List[Capability], List[str]]:

        found_capability_sets = list[CapabilitySet]()
        unmatched_values = OrderedSet[str](identifiers)
        found_capability_sets += self._rcs_service.find_by(unmatched_values.to_list(), query_builder_func)
        unmatched_values.remove_all([value_accessor(cs) for cs in found_capability_sets])

        found_capabilities = list[Capability]()
        found_capabilities += self._rc_service.find_by(unmatched_values.to_list(), query_builder_func)
        unmatched_values.remove_all([value_accessor(c) for c in found_capabilities])

        return found_capability_sets, found_capabilities, unmatched_values.to_list()

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
