from typing import List, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.report.http_request_result import HttpRequestResult
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import desc_long_cw, desc_med_cw, desc_short_cw, type_cw, uuid_cw


class MigrationReportWorksheet(AbstractWorksheet[HttpRequestResult]):

    _columns = [
        Column[HttpRequestResult](w=uuid_cw, n="Src Id", f=lambda x: x.srcEntityId),
        Column[HttpRequestResult](w=desc_short_cw, n="Src Name", f=lambda x: x.srcEntityName),
        Column[HttpRequestResult](w=desc_long_cw, n="Src Display Name", f=lambda x: x.srcEntityDisplayName),
        Column[HttpRequestResult](w=uuid_cw, n="Target Id", f=lambda x: x.tarEntityId),
        Column[HttpRequestResult](w=desc_short_cw, n="Target Name", f=lambda x: x.tarEntityName),
        Column[HttpRequestResult](w=desc_long_cw, n="Target Display Name", f=lambda x: x.tarEntityDisplayName),
        Column[HttpRequestResult](w=type_cw, n="Status", f=lambda x: x.status),
        Column[HttpRequestResult](w=desc_med_cw, n="Reason", f=lambda x: x.reason),
        Column[HttpRequestResult](w=type_cw, n="Error Http Status", f=lambda x: x.error and x.error.status),
        Column[HttpRequestResult](w=desc_long_cw, n="Error Message", f=lambda x: x.error and x.error.message),
        Column[HttpRequestResult](
            w=desc_long_cw, n="Error Response Body", f=lambda x: x.error and x.error.responseBody
        ),
    ]

    def __init__(self, ws: Worksheet, data: List[HttpRequestResult], title: str):
        super().__init__(ws, title, data, self._columns)

    @override
    def _get_row_fill_color(self, value: HttpRequestResult) -> PatternFill:
        if value.status == "error":
            return ws_constants.light_red_fill
        if value.status == "skipped" or value.status == "not_matched":
            return ws_constants.light_yellow_fill
        if value.status == "success":
            return ws_constants.light_green_fill
        return ws_constants.almost_white_fill
