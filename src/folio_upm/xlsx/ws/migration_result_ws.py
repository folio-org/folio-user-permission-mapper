from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.report.http_request_result import HttpRequestResult
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class MigrationReportWorksheet(AbstractWorksheet):

    _columns = [
        Column[HttpRequestResult](w=40, n="Src Id", f=lambda x: x.srcEntityId),
        Column[HttpRequestResult](w=40, n="Src Name", f=lambda x: x.srcEntityName),
        Column[HttpRequestResult](w=70, n="Src Display Name", f=lambda x: x.srcEntityDisplayName),
        Column[HttpRequestResult](w=40, n="Target Id", f=lambda x: x.tarEntityId),
        Column[HttpRequestResult](w=40, n="Target Name", f=lambda x: x.tarEntityName),
        Column[HttpRequestResult](w=70, n="Target Display Name", f=lambda x: x.tarEntityDisplayName),
        Column[HttpRequestResult](w=18, n="Status", f=lambda x: x.status),
        Column[HttpRequestResult](w=80, n="Reason", f=lambda x: x.reason),
        Column[HttpRequestResult](w=25, n="Error Http Status", f=lambda x: x.error and x.error.status),
        Column[HttpRequestResult](w=100, n="Error Message", f=lambda x: x.error and x.error.message),
        Column[HttpRequestResult](w=150, n="Error Response Body", f=lambda x: x.error and x.error.responseBody),
    ]

    def __init__(self, ws: Worksheet, data: List[HttpRequestResult], title: str):
        super().__init__(ws, title, data, self._columns)

    @override
    def _get_row_fill_color(self, call_rs: HttpRequestResult) -> Optional[PatternFill]:
        if call_rs.status == "error":
            return ws_constants.light_red_fill
        if call_rs.status == "skipped" or call_rs.status == "not_matched":
            return ws_constants.light_yellow_fill
        if call_rs.status == "success":
            return ws_constants.light_green_fill
        return ws_constants.almost_white_fill
