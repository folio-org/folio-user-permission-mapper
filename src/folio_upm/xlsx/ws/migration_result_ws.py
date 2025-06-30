from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.migration import EntityMigrationResult
from folio_upm.xlsx import constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class MigrationResultWorksheet(AbstractWorksheet):

    _columns = [
        Column[EntityMigrationResult](w=80, n="Entity Id", f=lambda x: x.entityId),
        Column[EntityMigrationResult](w=25, n="Entity Name", f=lambda x: x.entityName),
        Column[EntityMigrationResult](w=18, n="Status", f=lambda x: x.status),
        Column[EntityMigrationResult](w=40, n="Reason", f=lambda x: x.reason),
        Column[EntityMigrationResult](w=25, n="Error Http Status", f=lambda x: x.error and x.error.status),
        Column[EntityMigrationResult](w=100, n="Error Message", f=lambda x: x.error and x.error.message),
        Column[EntityMigrationResult](w=150, n="Error Response Body", f=lambda x: x.error and x.error.responseBody),
    ]

    def __init__(self, ws: Worksheet, title: str, data: List[EntityMigrationResult]):
        super().__init__(ws, title, data, self._columns)
        self._data = data

    @override
    def _get_row_fill_color(self, call_rs: EntityMigrationResult) -> Optional[PatternFill]:
        if call_rs.status == "error":
            return constants.light_red_fill
        if call_rs.status == "skipped" or call_rs.status == "not_matched":
            return constants.light_yellow_fill
        if call_rs.status == "success":
            return constants.light_green_fill
        return constants.almost_white_fill
