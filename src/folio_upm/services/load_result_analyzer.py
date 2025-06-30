from typing import Optional

from folio_upm.dto.results import AnalysisResult, LoadResult
from folio_upm.services.collectors.parent_perm_set_collector import ParentPermSetCollector
from folio_upm.services.collectors.perm_set_stats_collector import PermSetStatisticsCollector
from folio_upm.services.collectors.user_perm_set_collector import UserPermSetCollector
from folio_upm.services.collectors.user_stats_collector import UserStatsCollector
from folio_upm.services.permission_analyzer import PermissionAnalyzer
from folio_upm.services.roles_provider import RolesProvider
from folio_upm.utils import log_factory


class LoadResultAnalyzer:

    def __init__(self, analysis_json: dict, eureka_load_result=Optional[dict]):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("LoadResultAnalyzer initialized.")
        self._analysis_json = analysis_json
        self._lr = LoadResult(**analysis_json)
        self._eureka_lr = eureka_load_result
        self._ps_ar = PermissionAnalyzer(self._lr).get_analysis_result()
        self._result = self.__analyze_results()

    def get_results(self) -> AnalysisResult:
        return self._result

    def __analyze_results(self) -> AnalysisResult:
        load_result = self._lr
        ps_result = self._ps_ar
        roles_provider = RolesProvider(load_result, ps_result, self._eureka_lr)

        return AnalysisResult(
            userStatistics=UserStatsCollector(load_result, ps_result).get(),
            psStatistics=PermSetStatisticsCollector(ps_result).get(),
            userPermissionSets=UserPermSetCollector(load_result, ps_result).get(),
            permSetNesting=ParentPermSetCollector(load_result, ps_result).get(),
            roles=roles_provider.get_roles(),
            roleUsers=roles_provider.get_user_roles(),
            roleCapabilities=roles_provider.get_role_capabilities(),
        )
