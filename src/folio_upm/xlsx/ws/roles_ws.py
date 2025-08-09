from typing import Dict, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.analysis.analyzed_role import AnalyzedRole
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import bool_cw_short, num_short_cw, ps_name_cw, role_name_cw


class RolesWorksheet(AbstractWorksheet[AnalyzedRole]):

    _title = "Roles"
    _columns = [
        Column[AnalyzedRole](w=ps_name_cw, n="Name", f=lambda x: x.role.name),
        Column[AnalyzedRole](w=ps_name_cw, n="Source PS", f=lambda x: x.source),
        Column[AnalyzedRole](w=bool_cw_short, n="System", f=lambda x: str(x.systemGenerated).lower()),
        Column[AnalyzedRole](w=role_name_cw, n="Description", f=lambda x: x.role.description),
        Column[AnalyzedRole](w=num_short_cw, n="# Users", f=lambda x: x.usersCount),
        Column[AnalyzedRole](w=num_short_cw, n="# Capabilities", f=lambda x: x.capabilitiesCount),
        Column[AnalyzedRole](w=num_short_cw, n="# PS", f=lambda x: x.originalPermissionsCount),
        Column[AnalyzedRole](w=num_short_cw, n="# Total PS", f=lambda x: x.expandedPermissionsCount),
    ]

    def __init__(self, ws: Worksheet, data: Dict[str, AnalyzedRole]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_iterable_data(self):
        return self._data.values()

    @override
    def _get_row_fill_color(self, value: AnalyzedRole) -> PatternFill:
        if value.systemGenerated:
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill
