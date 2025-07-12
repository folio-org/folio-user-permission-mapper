from typing import List, Optional

from folio_upm.dto.eureka import UserRoles
from folio_upm.dto.results import AnalysisResult, EurekaLoadResult, OkapiLoadResult, PreparedEurekaData
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.services.collectors.parent_perm_set_collector import ParentPermSetCollector
from folio_upm.services.collectors.perm_set_stats_collector import PermSetStatisticsCollector
from folio_upm.services.collectors.user_perm_set_collector import UserPermSetCollector
from folio_upm.services.collectors.user_stats_collector import UserStatsCollector
from folio_upm.services.permission_analyzer import PermissionAnalyzer
from folio_upm.services.role_capabilities_provider import RoleCapabilitiesProvider
from folio_upm.services.roles_provider import RolesProvider
from folio_upm.services.user_roles_provider import UserRolesProvider
from folio_upm.utils import log_factory


class LoadResultAnalyzer:

    def __init__(self, okapi_load_rs: OkapiLoadResult, eureka_load_rs=Optional[EurekaLoadResult]):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LoadResultAnalyzer initialized.")
        self._analysis_json = okapi_load_rs
        self._okapi_lr = okapi_load_rs
        self._eureka_lr = eureka_load_rs
        self._ps_analysis_result = PermissionAnalyzer(self._okapi_lr).get_analysis_result()
        self._result = self.__analyze_results()

    def get_results(self) -> AnalysisResult:
        return self._result

    def get_prepared_eureka_data(self) -> PreparedEurekaData:
        return PreparedEurekaData(
            roles=list(self._result.roles.values()),
            roleUsers=self._result.roleUsers,
            roleCapabilities=self._result.roleCapabilities,
        )

    def __analyze_results(self) -> AnalysisResult:
        load_result = self._okapi_lr
        ps_ar = self._ps_analysis_result
        roles = RolesProvider(load_result, ps_ar).get_roles()
        user_roles = UserRolesProvider(ps_ar, roles).get_user_roles()
        role_capabilities = RoleCapabilitiesProvider(ps_ar, roles, self._eureka_lr).get_role_capabilities()

        self.__update_role_users_count(roles, user_roles)
        self.__update_role_capabilities_count(roles, role_capabilities)

        return AnalysisResult(
            userStatistics=UserStatsCollector(load_result, ps_ar).get(),
            psStatistics=PermSetStatisticsCollector(ps_ar, self._eureka_lr).get(),
            userPermissionSets=UserPermSetCollector(load_result, ps_ar).get(),
            permSetNesting=ParentPermSetCollector(load_result, ps_ar).get(),
            roles=roles,
            roleUsers=user_roles,
            roleCapabilities=role_capabilities,
        )

    @staticmethod
    def __update_role_users_count(roles, user_roles: List[UserRoles]):
        visited_users = set()
        for ur in user_roles:
            if ur.userId in visited_users:
                continue
            visited_users.add(ur.userId)
            for role_name in ur.roles:
                if role_name in roles:
                    roles[role_name].usersCount += 1

    @staticmethod
    def __update_role_capabilities_count(roles: dict, role_capabilities: List[RoleCapabilitiesHolder]):
        for rch in role_capabilities:
            if rch.roleName in roles:
                roles[rch.roleName].capabilitiesCount = len(rch.capabilities)
