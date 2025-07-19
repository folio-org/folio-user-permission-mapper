from folio_upm.dto.cleanup import HashRolesAnalysisResult
from folio_upm.xlsx.abstract_result_service import AbstractResultService, WsDef
from folio_upm.xlsx.ws.clean_hash_roles_ws import CleanHashRolesWorksheet
from folio_upm.xlsx.ws.eureka_role_capabilities_ws import EurekaRoleCapabilitiesWorksheet
from folio_upm.xlsx.ws.eureka_role_stats_ws import EurekaRoleStatsWorksheet
from folio_upm.xlsx.ws.eureka_role_users_ws import EurekaRoleUsersWorksheet
from folio_upm.xlsx.ws.eureka_user_stats_ws import EurekaUserStatsWorksheet


class EurekaXlsxReportProvider(AbstractResultService):

    _ws_defs = [
        WsDef(EurekaUserStatsWorksheet, lambda ar: ar.userStats),
        WsDef(EurekaRoleStatsWorksheet, lambda ar: ar.roleStats),
        WsDef(EurekaRoleUsersWorksheet, lambda ar: ar.userRoles),
        WsDef(EurekaRoleCapabilitiesWorksheet, lambda ar: ar.roleCapabilities),
        WsDef(CleanHashRolesWorksheet, lambda ar: ar.cleanHashRoles),
    ]

    def __init__(self, analysis_result: HashRolesAnalysisResult):
        super().__init__(analysis_result, self._ws_defs)
