from collections import OrderedDict
from typing import List, Optional
from typing import OrderedDict as OrdDict

from folio_upm.dto.eureka import Role
from folio_upm.dto.permission_type import MUTABLE
from folio_upm.dto.results import AnalyzedRole, EurekaLoadResult, LoadResult, PermissionAnalysisResult
from folio_upm.dto.support import AnalyzedPermissionSet, ExpandedPermissionSet
from folio_upm.utils import log_factory
from folio_upm.utils.common_utils import IterableUtils
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.service_utils import ServiceUtils
from folio_upm.utils.system_roles_provider import SystemRolesProvider


class RolesProvider:

    def __init__(
        self,
        load_result: LoadResult,
        ps_analysis_result: PermissionAnalysisResult,
        eureka_load_result: Optional[EurekaLoadResult],
    ):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._load_result = load_result
        self._eureka_load_result = eureka_load_result
        self._ps_analysis_result = ps_analysis_result
        self._log.info("Generating roles...")
        self._users_by_ps_names = self.__collect_users_by_ps_name()
        self._roles = self.__create_roles()
        self._log.info("Roles generated successfully.")

    def get_roles(self) -> OrdDict[str, AnalyzedRole]:
        return self._roles

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
            expandedPermissionsCount=self.__get_uq_sub_permission_count(expanded_sub_permissions),
            # will be populated later
            usersCount=0,
            capabilitiesCount=0,
        )

    def __get_user_roles(self):
        user_roles = OrderedDict()
        for ar in self._roles.values():
            for user in ar.users:
                if user not in user_roles:
                    user_roles[user] = OrderedSet()
                user_roles[user].add(ar.role.name)
        return user_roles

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
            if ps_type == MUTABLE:
                found_child_ap = self._ps_analysis_result[ps_type].get(permission_name, None)
                if found_child_ap is not None:
                    exp_list.append(permission_name)
                    result += self.__expand_sub_permissions(found_child_ap, exp_list=exp_list)
        return result

    @staticmethod
    def __get_uq_sub_permission_count(expanded_permissions: List[ExpandedPermissionSet]) -> int:
        unique_permissions = OrderedSet()
        for expanded_ps in expanded_permissions:
            unique_permissions.add(expanded_ps.permissionName)
        return len(unique_permissions)
