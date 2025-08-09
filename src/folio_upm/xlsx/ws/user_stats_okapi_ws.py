from typing import List, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.stats.permission_user_stats import PermissionUserStats
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import num_short_cw, uuid_cw


class UserStatsWorksheet(AbstractWorksheet[PermissionUserStats]):

    _title = "UserStats-Okapi"
    _columns = [
        Column[PermissionUserStats](w=uuid_cw, n="User Id", f=lambda x: x.userId),
        Column[PermissionUserStats](w=num_short_cw, n="# User-Created", f=lambda x: x.mutablePermissionSetsCount),
        Column[PermissionUserStats](w=num_short_cw, n="# Invalid", f=lambda x: x.invalidPermissionSetsCount),
        Column[PermissionUserStats](w=num_short_cw, n="# System-Created", f=lambda x: x.okapiPermissionSetsCount),
        Column[PermissionUserStats](w=num_short_cw, n="# Deprecated", f=lambda x: x.deprecatedPermissionSetsCount),
        Column[PermissionUserStats](w=num_short_cw, n="# Total", f=lambda x: x.allPermissionSetsCount),
    ]

    def __init__(self, ws: Worksheet, data: List[PermissionUserStats]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_row_fill_color(self, value: PermissionUserStats) -> PatternFill:
        if value.invalidPermissionSetsCount > 0:
            return ws_constants.light_red_fill
        if value.deprecatedPermissionSetsCount > 0:
            return ws_constants.light_yellow_fill
        if value.mutablePermissionSetsCount > 0:
            return ws_constants.light_green_fill
        return ws_constants.almost_white_fill

    def _get_iterable_data(self) -> List[PermissionUserStats]:
        return sorted(self._data, key=self.__get_sort_order)

    @staticmethod
    def __get_sort_order(user_stats: PermissionUserStats) -> tuple:
        return (
            -user_stats.mutablePermissionSetsCount,
            -user_stats.invalidPermissionSetsCount,
            -user_stats.okapiPermissionSetsCount,
        )
