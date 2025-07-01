from collections import OrderedDict
from typing import List, Optional
from typing import OrderedDict as OrdDict

from folio_upm.dto.eureka import Role, UserRoles
from folio_upm.dto.permission_type import MUTABLE
from folio_upm.dto.results import AnalyzedRole, EurekaLoadResult, LoadResult, PermissionAnalysisResult
from folio_upm.dto.support import (
    AnalyzedPermissionSet,
    CapabilityPlaceholder,
    ExpandedPermissionSet,
    RoleCapabilitiesHolder,
)
from folio_upm.services.capability_service import CapabilityService
from folio_upm.services.user_roles_provider import UserRolesProvider
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import IterableUtils
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.service_utils import ServiceUtils
from folio_upm.utils.system_roles_provider import SystemRolesProvider
from folio_upm.utils.upm_env import Env


class RolesProvider:

    def __init__(
        self,
        load_result: LoadResult,
        ps_analysis_result: PermissionAnalysisResult,
        eureka_load_result: Optional[EurekaLoadResult],
    ):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._load_result = load_result
        self._ps_analysis_result = ps_analysis_result
        self._capability_service = CapabilityService(eureka_load_result)
        self._users_by_ps_names = self.__collect_users_by_ps_name()
        self.__init_roles_and_relations()

    def get_roles(self) -> OrdDict[str, AnalyzedRole]:
        return self._roles

    def get_user_roles(self) -> List[UserRoles]:
        return self._user_roles

    def get_role_capabilities(self) -> List[RoleCapabilitiesHolder]:
        return self._role_capabilities

    def __init_roles_and_relations(self):
        self._log.info("Generating roles and their relationships...")
        self._roles = self.__create_roles()
        self._user_roles = UserRolesProvider(self._ps_analysis_result, self._roles).get_user_roles()
        self._role_capabilities = self.__create_role_capabilities()
        self._log.info("Roles and relationships generated successfully.")

    def __create_roles(self) -> OrdDict[str, AnalyzedRole]:
        result = OrderedDict[str, AnalyzedRole]()
        for analyzed_ps in self._ps_analysis_result.mutable.values():
            ar = self.__create_role(analyzed_ps)
            result[ar.role.name] = ar
        return result

    def __create_role(self, analyzed_ps: AnalyzedPermissionSet) -> AnalyzedRole | None:
        name = analyzed_ps.get_first_value(lambda x: x.displayName)
        description = analyzed_ps.get_first_value(lambda x: x.description)
        if description is not None:
            if len(description) >= 255:
                desc_for_log = description.replace("\n", "\\n")
                self._log.warning("Role description too long (max limit 255), shortening it: '%s'", desc_for_log)
                description = description and description[:245] + "..."
        else:
            description = ""

        role = Role(name=name and name.strip(), description=description)
        source_ps_name = analyzed_ps.permissionName

        expanded_sub_permissions = self.__expand_sub_permissions(analyzed_ps, [])

        is_system_generated = SystemRolesProvider().has_system_generated_ps(source_ps_name)
        if is_system_generated:
            role_name = SystemRolesProvider().get_eureka_role_name(source_ps_name)
            role = Role(name=role_name, description="System generated role")

        return AnalyzedRole(
            role=role,
            source=source_ps_name,
            users=self._users_by_ps_names.get(source_ps_name, OrderedSet()),
            permissionSets=expanded_sub_permissions,
            systemGenerated=is_system_generated,
            originalPermissionsCount=len(analyzed_ps.get_sub_permissions()),
            totalPermissionsCount=len(expanded_sub_permissions),
        )

    def __get_user_roles(self):
        user_roles = OrderedDict()
        for ar in self._roles.values():
            for user in ar.users:
                if user not in user_roles:
                    user_roles[user] = OrderedSet()
                user_roles[user].add(ar.role.name)
        return user_roles

    def __create_role_capabilities(self) -> List[RoleCapabilitiesHolder]:
        migration_strategy = Env().get_migration_strategy()
        role_capabilities = []
        for ar in self._roles.values():
            if ar.systemGenerated:
                continue
            capabilities_dict = OrderedDict[str, CapabilityPlaceholder]()
            role_permissions = ar.permissionSets
            for expanded_ps in role_permissions:
                capability = self.__create_role_capability(expanded_ps, migration_strategy)
                if capability is None:
                    continue
                if capability.permissionName not in capabilities_dict:
                    capabilities_dict[capability.permissionName] = capability
            capabilities = list(capabilities_dict.values())
            role_capabilities.append(RoleCapabilitiesHolder(roleName=ar.role.name, capabilities=capabilities))
        return role_capabilities

    def __collect_users_by_ps_name(self) -> dict[str, OrderedSet[str]]:
        users_by_ps_name = dict()
        for user_perm in self._load_result.allPermissionUsers:
            user_id = user_perm.userId
            for ps_name in user_perm.permissions:
                if ps_name not in users_by_ps_name:
                    users_by_ps_name[ps_name] = OrderedSet()
                users_by_ps_name[ps_name].add(user_id)
        return users_by_ps_name

    def __expand_sub_permissions(self, ap: AnalyzedPermissionSet, exp_list: List[str]) -> List[ExpandedPermissionSet]:
        result = []
        for permission_name in ap.get_sub_permissions():
            if permission_name in exp_list:
                continue
            if ServiceUtils.is_system_permission(permission_name):
                continue
            ps_type = self._ps_analysis_result.identify_permission_type(permission_name)
            expanded_from = IterableUtils.last(exp_list)
            result.append(ExpandedPermissionSet(permissionName=permission_name, expandedFrom=expanded_from))
            if ps_type == "mutable":
                found_child_ap = self._ps_analysis_result[ps_type].get(permission_name, None)
                if found_child_ap is not None:
                    exp_list.append(permission_name)
                    result += self.__expand_sub_permissions(found_child_ap, exp_list=exp_list)
        return result

    def __create_role_capability(self, expanded_ps, strategy: str):
        if strategy == "consolidated":
            ps_name = expanded_ps.permissionName
            permission_type = self._ps_analysis_result.identify_permission_type(ps_name)
            if permission_type != MUTABLE:
                return self.__create_capability_placeholder(expanded_ps, permission_type)
            else:
                return None
        if strategy == "distributed":
            if expanded_ps.expandedFrom is None:
                ps_name = expanded_ps.permissionName
                permission_type = self._ps_analysis_result.identify_permission_type(ps_name)
                if permission_type != MUTABLE:
                    return self.__create_capability_placeholder(expanded_ps, permission_type)
            else:
                return None
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
