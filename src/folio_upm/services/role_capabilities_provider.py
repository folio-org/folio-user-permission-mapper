from typing import Dict, List, Optional, Tuple

from folio_upm.model.analysis.analyzed_capability import AnalyzedCapability
from folio_upm.model.analysis.analyzed_role import AnalyzedRole
from folio_upm.model.analysis.analyzed_role_capabilities import AnalyzedRoleCapabilities
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.model.result.permission_analysis_result import PermissionAnalysisResult
from folio_upm.model.support.expanded_permission_set import ExpandedPermissionSet
from folio_upm.model.types.eureka_load_strategy import EurekaLoadStrategy
from folio_upm.model.types.permission_type import MUTABLE, PermissionType
from folio_upm.services.capability_service import CapabilityService
from folio_upm.services.extra_permissions_service import ExtraPermissionsService
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.upm_env import Env


class RoleCapabilitiesProvider:

    def __init__(
        self,
        ps_analysis_result: PermissionAnalysisResult,
        roles: Dict[str, AnalyzedRole],
        eureka_load_result: Optional[EurekaLoadResult],
    ):

        self._log = log_factory.get_logger(self.__class__.__name__)
        self._roles = roles
        self._ps_analysis_result = ps_analysis_result
        self._not_found_permission_sets = OrderedSet[str]()
        self._capability_service = CapabilityService(eureka_load_result)
        self._role_capabilities = self.__collect_role_capabilities()

    def get_role_capabilities(self) -> List[AnalyzedRoleCapabilities]:
        return self._role_capabilities

    def __collect_role_capabilities(self) -> List[AnalyzedRoleCapabilities]:
        migration_strategy = Env().get_migration_strategy()
        role_capabilities = list[AnalyzedRoleCapabilities]()
        for ar in self._roles.values():
            role_capabilities_holder = self.__process_single_role(ar, migration_strategy)
            if role_capabilities_holder:
                role_capabilities.append(role_capabilities_holder)

        not_found_ps_sets = self._not_found_permission_sets.to_list()
        if not_found_ps_sets:
            self._log.warning("The following permission sets were not found: %s", not_found_ps_sets)

        return role_capabilities

    def __process_single_role(self, ar: AnalyzedRole, migration_strategy) -> Optional[AnalyzedRoleCapabilities]:
        if ar.systemGenerated:
            return None
        capabilities_by_ps_name = dict[str, AnalyzedCapability]()
        visited_ps_names=  OrderedSet[str]()
        for expanded_ps in ar.permissionSets:
            capabilities = self.__create_role_capability(expanded_ps, migration_strategy)
            for capability in capabilities:
                if capability.permissionName not in capabilities_by_ps_name:
                    capabilities_by_ps_name[capability.permissionName] = capability
                else:
                    visited_ps_names.add(capability.permissionName)
        if visited_ps_names.to_list():
            self._log.debug("Role '%s' has duplicated capabilities: %s", ar.role.name, visited_ps_names.to_list())
        capabilities = list(capabilities_by_ps_name.values())
        extra_ps_names = ExtraPermissionsService().find_extra_ps_names(capabilities)
        for extra_ps_name in extra_ps_names:
            if extra_ps_name in capabilities_by_ps_name:
                continue
            permission_type = self._ps_analysis_result.identify_permission_type(extra_ps_name)
            expanded_ps = ExpandedPermissionSet(permissionName=extra_ps_name, expandedFrom=[])
            placeholder = self.__create_capability_placeholder(expanded_ps, permission_type)
            capabilities_by_ps_name[extra_ps_name] = placeholder
        return AnalyzedRoleCapabilities(roleName=ar.role.name, capabilities=list(capabilities_by_ps_name.values()))

    def __create_role_capability(self, expanded_ps, strategy: EurekaLoadStrategy) -> List[AnalyzedCapability]:
        if strategy == EurekaLoadStrategy.CONSOLIDATED:
            return self.__get_consolidated_capabilities(expanded_ps)
        return self.__get_distributed_capabilities(expanded_ps)

    def __get_distributed_capabilities(self, expanded_ps) -> List[AnalyzedCapability]:
        if len(expanded_ps.expandedFrom) == 0:
            ps_name = expanded_ps.permissionName
            permission_type = self._ps_analysis_result.identify_permission_type(ps_name)
            if permission_type != MUTABLE:
                return self.__convert_to_capability_placeholders(expanded_ps, permission_type)
        return []

    def __get_consolidated_capabilities(self, expanded_ps) -> List[AnalyzedCapability]:
        ps_name = expanded_ps.permissionName
        permission_type = self._ps_analysis_result.identify_permission_type(ps_name)
        if permission_type != MUTABLE:
            return self.__convert_to_capability_placeholders(expanded_ps, permission_type)
        return []

    def __convert_to_capability_placeholders(
        self, expanded_ps: ExpandedPermissionSet, ps_type: PermissionType
    ) -> List[AnalyzedCapability]:

        ps_name = expanded_ps.permissionName
        analyzed_ps = self._ps_analysis_result.get(ps_type).get(ps_name, None)
        expanded_pss = [(expanded_ps, ps_type)]

        if analyzed_ps is not None:
            expanded_pss += self.__get_nested_capability_sets(analyzed_ps)
        else:
            self._not_found_permission_sets.add(ps_name)

        capability_placeholders = []
        for ps, ps_type in expanded_pss:
            capability_placeholders.append(self.__create_capability_placeholder(ps, ps_type))
        return capability_placeholders

    def __create_capability_placeholder(self, expanded_ps, permission_type) -> AnalyzedCapability:
        permission_name = expanded_ps.permissionName

        analyzed_ps = self._ps_analysis_result.get(permission_type).get(permission_name, None)
        capability_or_set, resolved_type = self._capability_service.find_by_ps_name(permission_name)
        return AnalyzedCapability(
            resolvedType=resolved_type,
            permissionName=permission_name,
            permissionType=permission_type.get_name(),
            expandedFrom=expanded_ps.expandedFrom,
            displayName=analyzed_ps.get_uq_display_names_str() if analyzed_ps else None,
            name=capability_or_set.name if capability_or_set else None,
            resource=capability_or_set.resource if capability_or_set else None,
            action=capability_or_set.action if capability_or_set else None,
            capabilityType=capability_or_set.capabilityType if capability_or_set else None,
        )

    def __get_nested_capability_sets(self, analyzed_ps) -> List[Tuple[ExpandedPermissionSet, PermissionType]]:
        expanded_pss = []
        for sub_ps_name in analyzed_ps.get_sub_permissions(include_flat=True):
            sub_ps_type = self._ps_analysis_result.identify_permission_type(sub_ps_name)

            sub_analyzed_ps = self._ps_analysis_result.get(sub_ps_type).get(sub_ps_name, None)
            if sub_analyzed_ps is None:
                self._not_found_permission_sets.add(sub_ps_name)
                continue
            if sub_analyzed_ps.get_sub_permissions():
                expanded_sub_ps = ExpandedPermissionSet(permissionName=sub_ps_name, expandedFrom=[sub_ps_name])

                expanded_pss.append((expanded_sub_ps, sub_ps_type))
        return expanded_pss
