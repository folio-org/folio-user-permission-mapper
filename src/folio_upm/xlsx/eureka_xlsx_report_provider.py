from openpyxl import Workbook

from folio_upm.dto.clean_up import HashRolesAnalysisResult
from folio_upm.dto.results import AnalysisResult
from folio_upm.utils import log_factory
from folio_upm.xlsx.abstract_result_service import AbstractResultService, WsDef
from folio_upm.xlsx.ws.eureka_role_stats_ws import EurekaRoleStatsWorksheet
from folio_upm.xlsx.ws.eureka_user_stats_ws import EurekaUserStatsWorksheet
from folio_upm.xlsx.ws.ps_nesting_ws import PermissionNestingWorksheet
from folio_upm.xlsx.ws.ps_stats_ws import PermissionStatsWorksheet
from folio_upm.xlsx.ws.role_capabilities_ws import RolesCapabilitiesWorksheet
from folio_upm.xlsx.ws.roles_ws import RolesWorksheet
from folio_upm.xlsx.ws.user_ps import UserPermissionSetsWorksheet
from folio_upm.xlsx.ws.user_roles import UserRolesWorksheet
from folio_upm.xlsx.ws.user_stats_ws import UserStatsWorksheet


class EurekaXlsxReportProvider(AbstractResultService):

    _ws_defs = [
        WsDef(EurekaUserStatsWorksheet, lambda ar: ar.userStats),
        WsDef(EurekaRoleStatsWorksheet, lambda ar: ar.roleStats),
    ]

    def __init__(self, analysis_result: HashRolesAnalysisResult):
        super().__init__(analysis_result, self._ws_defs)
