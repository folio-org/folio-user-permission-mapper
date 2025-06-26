import uuid
from collections import OrderedDict
from typing import List
from typing import OrderedDict as OrdDict

from folio_upm.dto.capability_type import UNKNOWN
from folio_upm.dto.eureka import Role, RoleUsers
from folio_upm.dto.results import AnalyzedRole, EurekaLoadResult, LoadResult, PermissionAnalysisResult
from folio_upm.dto.strategy_type import DISTRIBUTED, StrategyType
from folio_upm.dto.support import (
    AnalyzedPermissionSet,
    CapabilityPlaceholder,
    ExpandedPermissionSet,
    RoleCapabilitiesHolder,
)
from folio_upm.utils import log_factory
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.service_utils import ServiceUtils


class RolesProvider:

    def __init__(
        self,
        load_result: LoadResult,
        ps_analysis_result: PermissionAnalysisResult,
        eureka_load_result: EurekaLoadResult = None,
        strategy: StrategyType = DISTRIBUTED,
    ):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._load_result = load_result
        self._eureka_load_result = eureka_load_result
        self._ps_analysis_result = ps_analysis_result
        self._strategy = strategy
        self._users_by_ps_names = self.__collect_users_by_ps_name()
        self.__init_roles_and_relations()

    def get_roles(self) -> OrdDict[str, AnalyzedRole]:
        return self._roles

    def get_role_users(self) -> List[RoleUsers]:
        return self._role_users

    def get_role_capabilities(self) -> List[RoleCapabilitiesHolder]:
        return self._role_capabilities

    def __init_roles_and_relations(self):
        self._log.info("Generating roles and their relationships...")
        self._roles = self.__create_roles()
        self._role_users = self.__collect_role_users()
        self._role_capabilities = self.__create_role_capabilities()
        self._log.info("Roles and relationships generated successfully.")

    def __create_roles(self) -> OrdDict[str, AnalyzedRole]:
        result = OrderedDict[str, AnalyzedRole]()
        for analyzed_ps in self._ps_analysis_result.mutable.values():
            ar = self.__create_role(analyzed_ps)
            result[ar.role.id] = ar
        return result

    def __create_role(self, analyzed_ps: AnalyzedPermissionSet) -> AnalyzedRole:
        name = analyzed_ps.get_first_value(lambda x: x.displayName)
        description = analyzed_ps.get_first_value(lambda x: x.description)
        role = Role(id=str(uuid.uuid4()), name=name, description=description)
        source_ps_name = analyzed_ps.permissionName

        expanded_sub_permissions = self.__expand_sub_permissions(analyzed_ps, [])

        return AnalyzedRole(
            role=role,
            source=source_ps_name,
            users=self._users_by_ps_names.get(source_ps_name, OrderedSet()),
            permissionSets=expanded_sub_permissions,
            excluded=False,
            originalPermissionsCount=len(analyzed_ps.get_sub_permissions()),
            totalPermissionsCount=len(expanded_sub_permissions),
        )

    def __collect_role_users(self) -> List[RoleUsers]:
        return [
            RoleUsers(roleId=role.role.id, userIds=list(role.users), roleName=role.role.name)
            for role in self._roles.values()
        ]

    def __create_role_capabilities(self) -> List[RoleCapabilitiesHolder]:
        return [self.__create_role_capability_holder(role) for role in self._roles.values()]

    def __create_role_capability_holder(self, role: AnalyzedRole) -> RoleCapabilitiesHolder:
        return RoleCapabilitiesHolder(
            roleId=role.role.id,
            roleName=role.role.name,
            capabilities=[self.__create_capability_placeholder(ps) for ps in role.permissionSets],
        )

    def __create_capability_placeholder(self, expanded_ps: ExpandedPermissionSet) -> CapabilityPlaceholder:
        permission_name = expanded_ps.permissionName
        permission_type = self._ps_analysis_result.identify_permission_type(permission_name)
        analyzed_ps = self._ps_analysis_result[permission_type].get(permission_name, None)
        return CapabilityPlaceholder(
            resolvedType=UNKNOWN,
            permissionName=permission_name,
            permissionType=permission_type,
            expandedFrom=expanded_ps.expandedFrom,
            displayName=analyzed_ps and analyzed_ps.get_uq_display_names_str(),
            # todo: collect this data from eureka capabilities
            name=None,
            resource=None,
            action=None,
            capabilityType=None,
        )

    def __collect_users_by_ps_name(self) -> dict[str, OrderedSet[str]]:
        users_by_ps_name = dict()
        for user_perm in self._load_result.allPermissionUsers:
            user_id = user_perm.userId
            for ps_name in user_perm.permissions:
                if ps_name not in users_by_ps_name:
                    users_by_ps_name[ps_name] = OrderedSet()
                users_by_ps_name[ps_name].append(user_id)
        return users_by_ps_name

    def __expand_sub_permissions(self, ap: AnalyzedPermissionSet, exp_list: List[str]) -> List[ExpandedPermissionSet]:
        result = []
        for permission_name in ap.get_sub_permissions():
            if permission_name in exp_list:
                continue
            ps_type = self._ps_analysis_result.identify_permission_type(permission_name)
            expanded_from = ServiceUtils.last(exp_list)
            result.append(ExpandedPermissionSet(permissionName=permission_name, expandedFrom=expanded_from))
            if ps_type == "mutable":
                found_child_ap = self._ps_analysis_result[ps_type].get(permission_name, None)
                if found_child_ap is not None:
                    exp_list.append(permission_name)
                    result += self.__expand_sub_permissions(found_child_ap, exp_list=exp_list)
        return result
