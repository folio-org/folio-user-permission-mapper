from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.permission_type import INVALID, MUTABLE, PermissionType
from folio_upm.dto.results import AnalyzedUserPermissionSet
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class UserPermissionSetsWorksheet(AbstractWorksheet):
    _title = "User-PS"
    _columns = [
        Column[AnalyzedUserPermissionSet](w=40, n="User Id", f=lambda x: x.userId),
        Column[AnalyzedUserPermissionSet](w=80, n="PS", f=lambda x: x.permissionName),
        Column[AnalyzedUserPermissionSet](w=80, n="PS Name", f=lambda x: x.displayName),
        Column[AnalyzedUserPermissionSet](w=25, n="PS Type", f=lambda x: x.get_permission_type_name()),
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
        if ps_type == INVALID:
            return ws_constants.light_red_fill
        if ps_type == MUTABLE:
            return ws_constants.light_green_fill
        if ps_type in self._yellow_types:
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill

