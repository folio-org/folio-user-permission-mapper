from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.cleanup import EurekaUserStats
from folio_upm.dto.permission_type import DEPRECATED, QUESTIONABLE, UNPROCESSED
from folio_upm.dto.results import PsStatistics
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class EurekaUserStatsWorksheet(AbstractWorksheet):

    title = "User-Stats"

    _columns = [
        Column[EurekaUserStats](w=40, n="User Id", f=lambda x: x.userId),
        Column[EurekaUserStats](w=20, n="Skip role assignment", f=lambda x: x.toBeSkipped),
        Column[EurekaUserStats](w=20, n="# Roles", f=lambda x: x.totalRoles),
        Column[EurekaUserStats](w=20, n="# Hash-Roles", f=lambda x: x.hashRoles),
        Column[EurekaUserStats](w=25, n="# Role Capabilities", f=lambda x: x.roleCapabilities),
        Column[EurekaUserStats](w=30, n="# Role Capability Sets", f=lambda x: x.roleCapabilitySets),
        Column[EurekaUserStats](w=32, n="# Hash-Role Capabilities", f=lambda x: x.hashRoleCapabilities),
        Column[EurekaUserStats](w=36, n="# Hash-Role Capability Sets", f=lambda x: x.hashRoleCapabilitySets),
        Column[EurekaUserStats](w=25, n="# All Capabilities", f=lambda x: x.allCapabilities),
        Column[EurekaUserStats](w=28, n="# All Capability Sets", f=lambda x: x.allCapabilitySets),
    ]

    def __init__(self, ws: Worksheet, data: List[EurekaUserStats]):
        super().__init__(ws, self.title, data, self._columns)
        self._yellow_types = [x.get_name() for x in [DEPRECATED, QUESTIONABLE, UNPROCESSED]]

    @override
    def _get_row_fill_color(self, ps_stats: PsStatistics) -> Optional[PatternFill]:
        return ws_constants.almost_white_fill
