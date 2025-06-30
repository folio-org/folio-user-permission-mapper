from collections import OrderedDict
from typing import List, OrderedDict as OrdDict

from folio_upm.dto.eureka import UserRoles, RoleUsers
from folio_upm.dto.results import AnalyzedRole
from folio_upm.utils.ordered_set import OrderedSet
from folio_upm.utils.system_roles_provider import SystemRolesProvider
from folio_upm.utils.upm_env import Env


class UserRolesProvider:

    def __init__(self, ps_analysis_result, roles: OrdDict[str, AnalyzedRole]):
        self._ps_analysis_result = ps_analysis_result
        self._roles = roles
        self._user_roles = self.__collect_user_roles()

    def get_user_roles(self) -> List[UserRoles]:
        return self._user_roles

    def __collect_user_roles(self) -> List[UserRoles]:
        strategy = Env().get_migration_strategy()
        user_roles = self.__get_user_roles()
        if strategy == "consolidated":
            return self.get_consolidated_user_roles(user_roles)
        return [UserRoles(userId=user_id, roles=roles.to_list()) for user_id, roles in user_roles.items()]

    def __get_user_roles(self) -> OrdDict[str, OrderedSet[str]]:
        user_roles = OrderedDict()
        for ar in self._roles.values():
            for user in ar.users:
                if user not in user_roles:
                    user_roles[user] = OrderedSet()
                user_roles[user].add(ar.role.name)
        return user_roles

    def get_consolidated_user_roles(self, user_roles:  OrdDict[str, OrderedSet[str]]) -> List[UserRoles]:
        consolidated_user_roles = []
        for user_id, role_names in user_roles:
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
            consolidated_user_roles.append(UserRoles(userId=user_id, roles=new_role_names.to_list()))
        return consolidated_user_roles

    @staticmethod
    def __has_any_parent(all_role_names, parent_ps_names):
        for parent_ps_name in parent_ps_names:
            if parent_ps_name in all_role_names:
                return True
        return False
