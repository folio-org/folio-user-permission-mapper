from folio_upm.dto.results import AnalysisResult
from folio_upm.xlsx.abstract_result_service import AbstractResultService, WsDef
from folio_upm.xlsx.ws.ps_nesting_ws import PermissionNestingWorksheet
from folio_upm.xlsx.ws.ps_stats_ws import PermissionStatsWorksheet
from folio_upm.xlsx.ws.role_capabilities_ws import RolesCapabilitiesWorksheet
from folio_upm.xlsx.ws.roles_ws import RolesWorksheet
from folio_upm.xlsx.ws.user_ps import UserPermissionSetsWorksheet
from folio_upm.xlsx.ws.user_roles import UserRolesWorksheet
from folio_upm.xlsx.ws.user_stats_ws import UserStatsWorksheet


class PsXlsxReportProvider(AbstractResultService):

    _ws_defs = [
        WsDef(PermissionNestingWorksheet, lambda ar: ar.permSetNesting),
        WsDef(UserPermissionSetsWorksheet, lambda ar: ar.userPermissionSets),
        WsDef(RolesWorksheet, lambda ar: ar.roles),
        WsDef(UserRolesWorksheet, lambda ar: ar.roleUsers),
        WsDef(RolesCapabilitiesWorksheet, lambda ar: ar.roleCapabilities),
        WsDef(UserStatsWorksheet, lambda ar: ar.userStatistics),
        WsDef(PermissionStatsWorksheet, lambda ar: ar.psStatistics),
    ]

    def __init__(self, analysis_result: AnalysisResult):
        super().__init__(analysis_result, self._ws_defs)
