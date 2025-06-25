from typing import Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.xlsx import constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class UserPsWorksheet(AbstractWorksheet):
    _title = "User-PS"
    _columns = [
        Column(w=40, n="User Id", f=lambda x: x.role.id),
        Column(w=60, n="PS Name", f=lambda x: x.role.name),
        Column(w=60, n="PS Type", f=lambda x: x.role.name)
    ]

    def __init__(self, ws: Worksheet, data: OrdDict[str, AnalyzedRole]):
        super().__init__(ws, self._title, data, self._columns)


    @override
    def _get_iterable_data(self):
        return self._data.sourcedPermissionSet()

    @override
    def _get_row_fill_color(self, value: AnalyzedRole) -> Optional[PatternFill]:
        return constants.almost_white_fill
