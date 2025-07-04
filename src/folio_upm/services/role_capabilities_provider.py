from typing import Dict, List, Optional

from folio_upm.dto.eureka_load_strategy import CONSOLIDATED, DISTRIBUTED, EurekaLoadStrategy
from folio_upm.dto.permission_type import MUTABLE
from folio_upm.dto.results import AnalyzedRole, EurekaLoadResult, PermissionAnalysisResult
from folio_upm.dto.support import CapabilityPlaceholder, RoleCapabilitiesHolder
from folio_upm.services.capability_service import CapabilityService
from folio_upm.utils import log_factory
from folio_upm.utils.upm_env import Env


class RoleCapabilitiesProvider:

    def __init__(
        self,
        ps_analysis_result: PermissionAnalysisResult,
        roles: Dict[str, AnalyzedRole],
        eureka_load_result: EurekaLoadResult,
    ):
        self._log = log_factory.get_logger(__class__.__name__)
        self._roles = roles
        self._ps_analysis_result = ps_analysis_result
        self._capability_service = CapabilityService(eureka_load_result)
        self._role_capabilities = self.__collect_role_capabilities()

    def get_role_capabilities(self) -> List[RoleCapabilitiesHolder]:
        return self._role_capabilities

    def __collect_role_capabilities(self) -> List[RoleCapabilitiesHolder]:
        migration_strategy = Env().get_migration_strategy()
        role_capabilities = list[RoleCapabilitiesHolder]()
        for ar in self._roles.values():
            role_capabilities_holder = self.__process_single_role(ar, migration_strategy)
            if role_capabilities_holder:
                role_capabilities.append(role_capabilities_holder)
        return role_capabilities

    def __process_single_role(self, ar: AnalyzedRole, migration_strategy) -> Optional[RoleCapabilitiesHolder]:
        if ar.systemGenerated:
            return None
        capabilities_dict = dict[str, CapabilityPlaceholder]()
        role_permissions = ar.permissionSets
        for expanded_ps in role_permissions:
            capability = self.__create_role_capability(expanded_ps, migration_strategy)
            if capability is None:
                continue
            if capability.permissionName not in capabilities_dict:
                capabilities_dict[capability.permissionName] = capability
        capabilities = list(capabilities_dict.values())
        return RoleCapabilitiesHolder(roleName=ar.role.name, capabilities=capabilities)

    def __create_role_capability(self, expanded_ps, strategy: EurekaLoadStrategy) -> Optional[CapabilityPlaceholder]:
        if strategy == CONSOLIDATED:
            return self.__get_consolidated_capabilities(expanded_ps)
        if strategy == DISTRIBUTED:
            return self.__get_distributed_capabilities(expanded_ps)
        return None

    def __get_distributed_capabilities(self, expanded_ps) -> Optional[CapabilityPlaceholder]:
        if len(expanded_ps.expandedFrom) == 0:
            ps_name = expanded_ps.permissionName
            permission_type = self._ps_analysis_result.identify_permission_type(ps_name)
            if permission_type != MUTABLE:
                return self.__create_capability_placeholder(expanded_ps, permission_type)
        return None

    def __get_consolidated_capabilities(self, expanded_ps) -> Optional[CapabilityPlaceholder]:
        ps_name = expanded_ps.permissionName
        permission_type = self._ps_analysis_result.identify_permission_type(ps_name)
        if permission_type != MUTABLE:
            return self.__create_capability_placeholder(expanded_ps, permission_type)
        return None

    def __create_capability_placeholder(self, expanded_ps, permission_type):
        permission_name = expanded_ps.permissionName
        analyzed_ps = self._ps_analysis_result[permission_type].get(permission_name, None)
        capability_or_set, resolved_type = self._capability_service.find_by_ps_name(permission_name)
        return CapabilityPlaceholder(
            resolvedType=resolved_type,
            permissionName=permission_name,
            permissionType=permission_type.get_name(),
            expandedFrom=expanded_ps.expandedFrom,
            displayName=analyzed_ps and analyzed_ps.get_uq_display_names_str(),
            name=capability_or_set and capability_or_set.name,
            resource=capability_or_set and capability_or_set.resource,
            action=capability_or_set and capability_or_set.action,
            capabilityType=capability_or_set and capability_or_set.capability_type,
        )
