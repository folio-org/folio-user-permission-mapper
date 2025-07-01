from openpyxl import Workbook

from folio_upm.dto.results import AnalysisResult
from folio_upm.utils import log_factory
from folio_upm.xlsx.ws.ps_nesting_ws import PermissionNestingWorksheet
from folio_upm.xlsx.ws.ps_stats_ws import PermissionStatsWorksheet
from folio_upm.xlsx.ws.role_capabilities_ws import RolesCapabilitiesWorksheet
from folio_upm.xlsx.ws.user_roles import UserRolesWorksheet
from folio_upm.xlsx.ws.roles_ws import RolesWorksheet
from folio_upm.xlsx.ws.user_ps import UserPermissionSetsWorksheet
from folio_upm.xlsx.ws.user_stats_ws import UserStatsWorksheet


class PermissionResultService:

    _worksheet_definitions = [
        (PermissionNestingWorksheet, lambda ar: ar.permSetNesting),
        (UserPermissionSetsWorksheet, lambda ar: ar.userPermissionSets),
        (RolesWorksheet, lambda ar: ar.roles),
        (UserRolesWorksheet, lambda ar: ar.roleUsers),
        (RolesCapabilitiesWorksheet, lambda ar: ar.roleCapabilities),
        (UserStatsWorksheet, lambda ar: ar.userStatistics),
        (PermissionStatsWorksheet, lambda ar: ar.psStatistics),
    ]

    def __init__(self, analysis_result: AnalysisResult):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Initializing XlsxReportGenerator...")
        self._analysis_result = analysis_result
        self._wb = self.__generate_workbook()

    def generate_report(self) -> Workbook:
        return self._wb

    def __generate_workbook(self):
        self._log.info("Generating XLSX report...")
        wb = Workbook()
        wb.remove(wb.active)
        for ws_def in self._worksheet_definitions:
            ws_class, data_extractor = ws_def
            self._log.debug("Processing worksheet in '%s'", ws_class.__name__)
            ws_generator = ws_class(wb.create_sheet(), data_extractor(self._analysis_result))
            ws_generator.fill()
        self._log.info("XLSX report generated successfully.")
        return wb
