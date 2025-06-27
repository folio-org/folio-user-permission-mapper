from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.errors import HttpCallResult
from folio_upm.dto.results import PsStatistics
from folio_upm.xlsx import constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class MigrationResultWorksheet(AbstractWorksheet):

    title = "Roles"

    _columns = [
        Column[PsStatistics](w=40, n="Entity Id", f=lambda x: x.entityId),
        Column[PsStatistics](w=15, n="Entity Name", f=lambda x: x.entityName),
        Column[PsStatistics](w=18, n="status", f=lambda x: x.status),
        Column[PsStatistics](w=30, n="reason", f=lambda x: x.reason),
        Column[PsStatistics](w=30, n="Error Message", f=lambda x: x.error and x.error.message),
        Column[PsStatistics](w=15, n="Error Http Status", f=lambda x: x.error and x.error.status),
        Column[PsStatistics](w=80, n="Error Response Body", f=lambda x: x.error and x.error.responseBody)
    ]

    def __init__(self, ws: Worksheet, title: str, data: List[HttpCallResult]):
        super().__init__(ws, title, data, self._columns)
        self._data = data

    @override
    def _get_row_fill_color(self, call_rs: HttpCallResult) -> Optional[PatternFill]:
        if call_rs.status == "error":
            return constants.light_red_fill
        if call_rs.status == "skipped":
            return constants.light_yellow_fill
        if call_rs.status == "success":
            return constants.light_green_fill
        return constants.almost_white_fill
