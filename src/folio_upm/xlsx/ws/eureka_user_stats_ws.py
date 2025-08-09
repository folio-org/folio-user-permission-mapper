from typing import List

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.stats.eureka_user_stats import EurekaUserStats
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import num_long_cw, num_short_cw, uuid_cw


class EurekaUserStatsWorksheet(AbstractWorksheet[EurekaUserStats]):

    _columns = [
        Column[EurekaUserStats](w=uuid_cw, n="User Id", f=lambda x: x.userId),
        Column[EurekaUserStats](w=num_short_cw, n="# Roles", f=lambda x: x.totalRoles),
        Column[EurekaUserStats](w=num_short_cw, n="# Hash-Roles", f=lambda x: x.hashRoles),
        Column[EurekaUserStats](w=num_short_cw, n="# Role Capabilities", f=lambda x: x.roleCapabilities),
        Column[EurekaUserStats](w=num_long_cw, n="# Role Capability Sets", f=lambda x: x.roleCapabilitySets),
        Column[EurekaUserStats](w=num_long_cw, n="# Hash-Role Capabilities", f=lambda x: x.hashRoleCapabilities),
        Column[EurekaUserStats](w=num_long_cw, n="# Hash-Role Capability Sets", f=lambda x: x.hashRoleCapabilitySets),
        Column[EurekaUserStats](w=num_long_cw, n="# All Capabilities", f=lambda x: x.allCapabilities),
        Column[EurekaUserStats](w=num_long_cw, n="# All Capability Sets", f=lambda x: x.allCapabilitySets),
    ]

    def __init__(self, ws: Worksheet, data: List[EurekaUserStats]):
        title = "User-Stats"
        super().__init__(ws, title, data, self._columns)
