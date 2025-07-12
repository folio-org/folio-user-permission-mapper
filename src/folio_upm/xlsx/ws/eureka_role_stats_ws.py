from typing import List

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.clean_up import EurekaRoleStats
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class EurekaRoleStatsWorksheet(AbstractWorksheet):

    title = "Role-Stats"

    _columns = [
        Column[EurekaRoleStats](w=80, n="Role Id", f=lambda x: x.roleName),
        Column[EurekaRoleStats](w=80, n="Role Name", f=lambda x: x.roleName),
        Column[EurekaRoleStats](w=25, n="Hash-Role?", f=lambda x: x.isHashRole),
        Column[EurekaRoleStats](w=25, n="# Users", f=lambda x: x.totalUsers),
        Column[EurekaRoleStats](w=25, n="# Capabilities", f=lambda x: x.capabilitiesNum),
        Column[EurekaRoleStats](w=25, n="# Capability Sets", f=lambda x: x.capabilitySetsNum),
    ]

    def __init__(self, ws: Worksheet, data: List[EurekaRoleStats]):
        super().__init__(ws, self.title, data, self._columns)
