from typing import List, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.analysis.analyzed_user_roles import AnalyzedUserRoles
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import bool_cw_short, num_short_cw, uuid_cw


class UserRoleStatsWorksheet(AbstractWorksheet[AnalyzedUserRoles]):

    _columns = [
        Column[AnalyzedUserRoles](w=uuid_cw, n="User Id", f=lambda x: x.userId),
        Column[AnalyzedUserRoles](w=bool_cw_short, n="Skip Role Assignment", f=lambda x: x.skipRoleAssignment),
        Column[AnalyzedUserRoles](w=num_short_cw, n="# Roles", f=lambda x: len(x.roleNames or [])),
    ]

    def __init__(self, ws: Worksheet, data: List[AnalyzedUserRoles]):
        _title = "UserRoleStats-Eureka"
        super().__init__(ws, _title, data, self._columns)

    @override
    def _get_row_fill_color(self, value: AnalyzedUserRoles) -> PatternFill:
        if value.skipRoleAssignment:
            return ws_constants.light_red_fill
        return ws_constants.light_green_fill
