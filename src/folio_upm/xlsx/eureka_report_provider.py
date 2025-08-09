from folio_upm.model.result.hash_roles_analysis_result import HashRolesAnalysisResult
from folio_upm.xlsx.abstract_report_provider import AbstractReportProvider, WsDef
from folio_upm.xlsx.ws.clean_hash_role_stats_ws import CleanHashRoleStatsWorksheet
from folio_upm.xlsx.ws.clean_hash_roles_ws import CleanHashRolesWorksheet
from folio_upm.xlsx.ws.eureka_role_capabilities_ws import EurekaRoleCapabilitiesWorksheet
from folio_upm.xlsx.ws.eureka_role_stats_ws import EurekaRoleStatsWorksheet
from folio_upm.xlsx.ws.eureka_role_users_ws import EurekaRoleUsersWorksheet
from folio_upm.xlsx.ws.eureka_user_stats_ws import EurekaUserStatsWorksheet


class EurekaReportProvider(AbstractReportProvider):

    _ws_defs = [
        WsDef(EurekaUserStatsWorksheet, lambda ar: ar.userStats),
        WsDef(EurekaRoleStatsWorksheet, lambda ar: ar.roleStats),
        WsDef(EurekaRoleUsersWorksheet, lambda ar: ar.userRoles),
        WsDef(EurekaRoleCapabilitiesWorksheet, lambda ar: ar.roleCapabilities),
        WsDef(CleanHashRolesWorksheet, lambda ar: ar.hashRoleCleanupRecords),
        WsDef(CleanHashRoleStatsWorksheet, lambda ar: ar.hashRoleCleanupRecords),
    ]

    def __init__(self, analysis_result: HashRolesAnalysisResult):
        super().__init__(analysis_result, self._ws_defs)
