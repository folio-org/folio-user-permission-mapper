from openpyxl import Workbook
from openpyxl.styles import Border, Font, PatternFill, Side

from folio_upm.dto.results import AnalysisResult
from folio_upm.utils import log_factory
from folio_upm.xlsx.ws.ps_nesting_ws import PermissionNestingWorksheet
from folio_upm.xlsx.ws.ps_stats_ws import PermissionStatsWorksheet
from folio_upm.xlsx.ws.role_capabilities_ws import RolesCapabilitiesWorksheet
from folio_upm.xlsx.ws.role_users import RoleUsersWorksheet
from folio_upm.xlsx.ws.roles_ws import RolesWorksheet
from folio_upm.xlsx.ws.user_ps import UserPermissionSetsWorksheet
from folio_upm.xlsx.ws.user_stats_ws import UserStatsWorksheet

_light_green_fill = PatternFill(start_color="c6efe3", end_color="c6efe3", fill_type="darkHorizontal")
_light_red_fill = PatternFill(start_color="ffe1e5", end_color="ffe1e5", fill_type="darkHorizontal")
_list_yellow_fill = PatternFill(start_color="ffffcc", end_color="ffffcc", fill_type="darkHorizontal")
_thin_border = Border(
    left=Side(style="thin", color="bababa"),
    right=Side(style="thin", color="bababa"),
    top=Side(style="thin", color="bababa"),
    bottom=Side(style="thin", color="bababa"),
)

_cells_font = Font(name="Consolas", bold=False, italic=False, size=11)
_header_font = Font(name="Consolas", bold=True, size=11)


class ExcelResultGenerator:

    _worksheet_definitions = [
        (UserStatsWorksheet, lambda ar: ar.userStatistics),
        (PermissionStatsWorksheet, lambda ar: ar.psStatistics),
        (PermissionNestingWorksheet, lambda ar: ar.permSetNesting),
        (UserPermissionSetsWorksheet, lambda ar: ar.userPermissionSets),
        (RolesWorksheet, lambda ar: ar.roles),
        (RoleUsersWorksheet, lambda ar: ar.roleUsers),
        (RolesCapabilitiesWorksheet, lambda ar: ar.roleCapabilities),
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

        return wb
