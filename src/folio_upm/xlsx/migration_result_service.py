from openpyxl import Workbook

from folio_upm.dto.results import EurekaMigrationResult
from folio_upm.utils import log_factory
from folio_upm.xlsx.ws.migration_result_ws import MigrationResultWorksheet


class MigrationResultService:

    _worksheet_definitions = [
        ("Roles", lambda migration_rs: migration_rs.roles),
        ("Role-Users", lambda migration_rs: migration_rs.roleUsers),
        ("Role-Capabilities", lambda migration_rs: migration_rs.roleCapabilities),
    ]

    def __init__(self, migration_result: EurekaMigrationResult):
        self._log = log_factory.get_logger(self.__class__.__name__)
        self._log.debug("Initializing XlsxReportGenerator...")
        self._migration_result = migration_result
        self._wb = self.__generate_workbook()

    def generate_report(self) -> Workbook:
        return self._wb

    def __generate_workbook(self):
        self._log.info("Generating XLSX report...")
        wb = Workbook()
        wb.remove(wb.active)
        for ws_def in self._worksheet_definitions:
            title, data_extractor = ws_def
            self._log.debug("Processing worksheet in '%s': %s", MigrationResultWorksheet.__name__, title)
            ws_generator = MigrationResultWorksheet(wb.create_sheet(), title, data_extractor(self._migration_result))
            ws_generator.fill()

        return wb
