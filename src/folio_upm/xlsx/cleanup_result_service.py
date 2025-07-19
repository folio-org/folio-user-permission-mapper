from folio_upm.dto.results import EurekaMigrationResult, EurekaCleanUpResult
from folio_upm.xlsx.abstract_result_service import AbstractResultService, WsDef
from folio_upm.xlsx.ws.migration_result_ws import MigrationResultWorksheet


class CleanupResultService(AbstractResultService):

    _ws_defs = [
        WsDef(MigrationResultWorksheet, lambda d: d.roles, "Roles"),
        WsDef(MigrationResultWorksheet, lambda d: d.roleCapabilities, "Role-Capabilities"),
    ]

    def __init__(self, migration_result: EurekaCleanUpResult):
        super().__init__(migration_result, self._ws_defs)
