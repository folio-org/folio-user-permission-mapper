from typing import List

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.stats.eureka_role_stats import EurekaRoleStats
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import bool_long_cw, num_short_cw, role_id_cw, role_name_cw


class EurekaRoleStatsWorksheet(AbstractWorksheet):

    _columns = [
        Column[EurekaRoleStats](w=role_id_cw, n="Role Id", f=lambda x: x.roleId),
        Column[EurekaRoleStats](w=role_name_cw, n="Role Name", f=lambda x: x.roleName),
        Column[EurekaRoleStats](w=bool_long_cw, n="Hash-Role?", f=lambda x: x.isHashRole),
        Column[EurekaRoleStats](w=num_short_cw, n="# Users", f=lambda x: x.totalUsers),
        Column[EurekaRoleStats](w=num_short_cw, n="# Capabilities", f=lambda x: x.capabilitiesNum),
        Column[EurekaRoleStats](w=num_short_cw, n="# Capability Sets", f=lambda x: x.capabilitySetsNum),
    ]

    def __init__(self, ws: Worksheet, data: List[EurekaRoleStats]):
        _title = "Role-Stats"
        super().__init__(ws, _title, data, self._columns)
