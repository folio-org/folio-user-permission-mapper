from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.analysis.analyzed_user_roles import AnalyzedUserRoles
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class UserRoleStatsWorksheet(AbstractWorksheet):

    _title = "UserRoleStats-Eureka"
    _columns = [
        Column[AnalyzedUserRoles](w=40, n="User Id", f=lambda x: x.userId),
        Column[AnalyzedUserRoles](w=20, n="Skip Role Assignment", f=lambda x: x.skipRoleAssignment),
        Column[AnalyzedUserRoles](w=20, n="# Roles", f=lambda x: len(x.roleNames or [])),
    ]

    def __init__(self, ws: Worksheet, data: List[AnalyzedUserRoles]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_row_fill_color(self, user_roles: AnalyzedUserRoles) -> Optional[PatternFill]:
        if user_roles.skipRoleAssignment:
            return ws_constants.light_red_fill
        return ws_constants.light_green_fill
