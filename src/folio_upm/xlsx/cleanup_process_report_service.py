from folio_upm.model.report.hash_roles_cleanup_report import HashRolesCleanupReport
from folio_upm.xlsx.abstract_result_service import AbstractReportProvider, WsDef
from folio_upm.xlsx.ws.migration_result_ws import MigrationReportWorksheet


class CleanupProcessReportProvider(AbstractReportProvider):

    _ws_defs = [
        WsDef(MigrationReportWorksheet, lambda d: d.roles, "Roles"),
        WsDef(MigrationReportWorksheet, lambda d: d.roleCapabilities, "Role-Capabilities"),
    ]

    def __init__(self, cleanup_report: HashRolesCleanupReport):
        super().__init__(cleanup_report, self._ws_defs)
