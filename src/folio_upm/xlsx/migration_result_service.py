from folio_upm.dto.results import EurekaMigrationResult
from folio_upm.xlsx.abstract_result_service import AbstractResultService, WsDef
from folio_upm.xlsx.ws.migration_result_ws import MigrationResultWorksheet


class MigrationResultService(AbstractResultService):

    _ws_defs = [
        WsDef(MigrationResultWorksheet, lambda d: d.roles, "Roles"),
        WsDef(MigrationResultWorksheet, lambda d: d.roleUsers, "Role-Users"),
        WsDef(MigrationResultWorksheet, lambda d: d.roleCapabilities, "Role-Capabilities"),
    ]

    def __init__(self, migration_result: EurekaMigrationResult):
        super().__init__(migration_result, self._ws_defs)
