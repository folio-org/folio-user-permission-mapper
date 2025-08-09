from folio_upm.model.report.eureka_migration_report import EurekaMigrationReport
from folio_upm.xlsx.abstract_report_provider import AbstractReportProvider, WsDef
from folio_upm.xlsx.ws.migration_result_ws import MigrationReportWorksheet


class MigrationProcessReportProvider(AbstractReportProvider):

    _ws_defs = [
        WsDef(MigrationReportWorksheet, lambda d: d.roles, "Roles"),
        WsDef(MigrationReportWorksheet, lambda d: d.roleUsers, "Role-Users"),
        WsDef(MigrationReportWorksheet, lambda d: d.roleCapabilities, "Role-Capabilities"),
    ]

    def __init__(self, migration_result: EurekaMigrationReport):
        super().__init__(migration_result, self._ws_defs)
