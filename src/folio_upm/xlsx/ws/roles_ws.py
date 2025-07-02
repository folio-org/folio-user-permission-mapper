from typing import Optional
from typing import OrderedDict as OrdDict
from typing import override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.results import AnalyzedRole
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class RolesWorksheet(AbstractWorksheet):

    _title = "Roles"
    _columns = [
        Column[AnalyzedRole](w=60, n="Name", f=lambda x: x.role.name),
        Column[AnalyzedRole](w=50, n="Source PS", f=lambda x: x.source),
        Column[AnalyzedRole](w=14, n="System", f=lambda x: str(x.systemGenerated).lower()),
        Column[AnalyzedRole](w=60, n="Description", f=lambda x: x.role.description),
        Column[AnalyzedRole](w=22, n="# Users", f=lambda x: x.usersCount),
        Column[AnalyzedRole](w=22, n="# Capabilities", f=lambda x: x.capabilitiesCount),
        Column[AnalyzedRole](w=22, n="# PS", f=lambda x: x.originalPermissionsCount),
        Column[AnalyzedRole](w=22, n="# Total PS", f=lambda x: x.expandedPermissionsCount),
    ]

    def __init__(self, ws: Worksheet, data: OrdDict[str, AnalyzedRole]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_iterable_data(self):
        return self._data.values()

    @override
    def _get_row_fill_color(self, value: AnalyzedRole) -> Optional[PatternFill]:
        if value.systemGenerated:
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill
