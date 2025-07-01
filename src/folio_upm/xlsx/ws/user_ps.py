from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.results import AnalyzedUserPermissionSet
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class UserPermissionSetsWorksheet(AbstractWorksheet):
    _title = "User-PS"
    _columns = [
        Column(w=40, n="User Id", f=lambda x: x.userId),
        Column(w=80, n="PS Name", f=lambda x: x.psName),
        Column(w=15, n="PS Type", f=lambda x: x.psType),
    ]

    def __init__(self, ws: Worksheet, data: List[AnalyzedUserPermissionSet]):
        super().__init__(ws, self._title, data, self._columns)
        self._yellow_types = ["deprecated", "questionable", "unprocessed"]

    @override
    def _get_iterable_data(self):
        return self._data

    @override
    def _get_row_fill_color(self, value: AnalyzedUserPermissionSet) -> Optional[PatternFill]:
        ps_type = value.psType
        if ps_type == "invalid":
            return ws_constants.light_red_fill
        if ps_type == "mutable":
            return ws_constants.light_green_fill
        if ps_type in self._yellow_types:
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill
