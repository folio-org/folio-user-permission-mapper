from typing import List, Optional

from folio_upm.model.analysis.analyzed_role_capabilities import AnalyzedRoleCapabilities
from folio_upm.model.analysis.analyzed_user_roles import AnalyzedUserRoles
from folio_upm.model.load.eureka_load_result import EurekaLoadResult
from folio_upm.model.load.okapi_load_result import OkapiLoadResult
from folio_upm.model.result.eureka_migration_data import EurekaMigrationData
from folio_upm.model.result.okapi_analysis_result import OkapiAnalysisResult
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
    """
    Analyzes FOLIO permission data and generates comprehensive analysis results.

    This class processes Okapi and Eureka load results to analyze user permissions,
    roles, and capabilities. It consolidates data from multiple sources to provide
    statistics, role mappings, and migration data for FOLIO systems.

    Attributes:
        _log: Logger instance for debugging and information messages
        _okapi_lr: Okapi load result containing permission and user data
        _eureka_lr: Optional Eureka load result for additional capability data
        _ps_analysis_result: Analyzed permission set data from PermissionAnalyzer
        _result: Final OkapiAnalysisResult containing all analyzed data

    Example:
        >>> okapi_result = OkapiLoadResult(...)
        >>> eureka_result = EurekaLoadResult(...)
        >>> analyzer = LoadResultAnalyzer(okapi_result, eureka_result)
        >>> analysis = analyzer.get_results()
        >>> migration_data = analyzer.get_eureka_migration_data()
    """

    def __init__(self, okapi_load_rs: OkapiLoadResult, eureka_load_rs: Optional[EurekaLoadResult]):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LoadResultAnalyzer initialized.")
        self._analysis_json = okapi_load_rs
        self._okapi_lr = okapi_load_rs
        self._eureka_lr = eureka_load_rs
        self._ps_analysis_result = PermissionAnalyzer(self._okapi_lr).get_analysis_result()
        self._result = self.__analyze_results()

    def get_results(self) -> OkapiAnalysisResult:
        """
        Returns the complete analysis results for the Okapi load data.

        Provides comprehensive analysis including user statistics, permission set statistics,
        user permission mappings, permission set nesting, roles, user roles, and role capabilities.

        Returns:
            OkapiAnalysisResult: Complete analysis result containing all processed data
                including statistics, mappings, and role information.
        """
        return self._result

    def get_eureka_migration_data(self) -> EurekaMigrationData:
        """
        Extracts and returns migration data specifically formatted for Eureka systems.

        Consolidates roles, user roles, and role capabilities into a format suitable
        for migrating permission data to Eureka-based systems.

        Returns:
            EurekaMigrationData: Migration-ready data containing roles as a list,
                user role assignments, and role capability mappings.
        """
        return EurekaMigrationData(
            roles=list(self._result.roles.values()),
            userRoles=self._result.userRoles,
            roleCapabilities=self._result.roleCapabilities,
        )

    def __analyze_results(self) -> OkapiAnalysisResult:
        load_result = self._okapi_lr
        ps_ar = self._ps_analysis_result
        roles = RolesProvider(load_result, ps_ar).get_roles()
        user_roles = UserRolesProvider(ps_ar, roles).get_user_roles()

        role_capabilities = RoleCapabilitiesProvider(ps_ar, roles, self._eureka_lr).get_role_capabilities()

        self.__update_role_users_count(roles, user_roles)
        self.__update_role_capabilities_count(roles, role_capabilities)

        return OkapiAnalysisResult(
            userStatistics=UserStatsCollector(load_result, ps_ar).get(),
            psStatistics=PermSetStatisticsCollector(ps_ar, self._eureka_lr).get(),
            userPermissionSets=UserPermSetCollector(load_result, ps_ar).get(),
            permSetNesting=ParentPermSetCollector(load_result, ps_ar).get(),
            roles=roles,
            userRoles=user_roles,
            roleCapabilities=role_capabilities,
        )

    @staticmethod
    def __update_role_users_count(roles, user_roles: List[AnalyzedUserRoles]):
        visited_users = set()
        for ur in user_roles:
            if ur.userId in visited_users:
                continue
            visited_users.add(ur.userId)

            for role_name in ur.roleNames:
                if role_name in roles:
                    roles[role_name].usersCount += 1

    @staticmethod
    def __update_role_capabilities_count(roles: dict, role_capabilities: List[AnalyzedRoleCapabilities]):
        for rch in role_capabilities:
            if rch.roleName in roles:
                roles[rch.roleName].capabilitiesCount = len(rch.capabilities)
