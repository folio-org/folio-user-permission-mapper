from typing import Dict, List

from folio_upm.dto.eureka import UserRoles
from folio_upm.dto.results import AnalyzedRole, PermissionAnalysisResult
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.system_roles_provider import SystemRolesProvider
from folio_upm.utils.upm_env import Env


class UserRolesProvider:

    def __init__(self, ps_analysis_result: PermissionAnalysisResult, roles: Dict[str, AnalyzedRole]):
        self._ps_analysis_result = ps_analysis_result
        self._roles = roles
        self._roles_by_ps_name = self.__collect_roles_by_src_ps_name()
        self._user_roles = self.__collect_user_roles()

    def get_user_roles(self) -> List[UserRoles]:
        return self._user_roles

    def __collect_user_roles(self) -> List[UserRoles]:
        strategy = Env().get_migration_strategy()
        user_roles = self.__get_user_roles()
        if strategy == "consolidated":
            return self.__get_consolidated_user_roles(user_roles)
        return self.__get_distributed_user_roles(user_roles)

    def __get_user_roles(self) -> Dict[str, OrderedSet[str]]:
        user_roles = {}
        for ar in self._roles.values():
            for user in ar.users:
                if user not in user_roles:
                    user_roles[user] = OrderedSet()
                user_roles[user].add(ar.role.name)
        return user_roles

    def __get_distributed_user_roles(self, user_roles: Dict[str, OrderedSet[str]]) -> List[UserRoles]:
        distributed_user_roles = []
        for user_id, role_names in user_roles.items():
            new_role_names = self.__get_distributed_role_names(role_names)
            distributed_user_roles.append(UserRoles(userId=user_id, roles=new_role_names.to_list()))
        return distributed_user_roles

    def __get_consolidated_user_roles(self, user_roles: Dict[str, OrderedSet[str]]) -> List[UserRoles]:
        consolidated_user_roles = []
        for user_id, role_names in user_roles.items():
            new_role_names = self.__get_consolidated_role_names(role_names)
            consolidated_user_roles.append(UserRoles(userId=user_id, roles=new_role_names.to_list()))
        return consolidated_user_roles

    def __get_distributed_role_names(self, role_names):
        new_role_names = OrderedSet()
        for role_name in role_names:
            role = self._roles.get(role_name)
            new_role_names.add(role_name)
            for expanded_ps in role.permissionSets:
                ps_name = expanded_ps.permissionName
                if SystemRolesProvider().has_system_generated_ps(ps_name):
                    new_role_names.add(SystemRolesProvider().get_eureka_role_name(ps_name))
                    continue
                if ps_name not in self._roles_by_ps_name:
                    continue
                matched_roles = self._roles_by_ps_name[ps_name]
                for matched_role in matched_roles:
                    new_role_names.add(matched_role.role.name)
        return new_role_names

    def __get_consolidated_role_names(self, role_names):
        new_role_names = OrderedSet()
        all_role_names = OrderedSet(role_names)
        for role_name in role_names:
            role = self._roles.get(role_name)
            src_ps_name = role.source
            if SystemRolesProvider().has_system_generated_ps(src_ps_name):
                new_role_names.add(role_name)
                continue
            permission_type = self._ps_analysis_result.identify_permission_type(src_ps_name)
            analyzed_permission = self._ps_analysis_result[permission_type].get(src_ps_name)
            parent_ps_names = analyzed_permission.get_parent_permission_names()
            if not self.__has_any_parent(all_role_names, parent_ps_names):
                new_role_names.add(role_name)
        return new_role_names

    def __collect_roles_by_src_ps_name(self) -> Dict[str, List[AnalyzedRole]]:
        roles_by_ps_name = dict[str, List[AnalyzedRole]]()
        for role in self._roles.values():
            src_ps_name = role.source
            if src_ps_name not in roles_by_ps_name:
                roles_by_ps_name[src_ps_name] = []
            roles_by_ps_name[src_ps_name].append(role)
        return roles_by_ps_name

    @staticmethod
    def __has_any_parent(all_role_names, parent_ps_names):
        for parent_ps_name in parent_ps_names:
            if parent_ps_name in all_role_names:
                return True
        return False
