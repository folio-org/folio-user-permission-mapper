from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.results import UserStatistics
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class UserStatsWorksheet(AbstractWorksheet):

    _title = "User Stats"
    _columns = [
        Column(w=40, n="User Id", f=lambda x: x.userId),
        Column(w=21, n="# of Mutable", f=lambda x: x.mutablePermissionSetsCount),
        Column(w=21, n="# of Invalid", f=lambda x: x.invalidPermissionSetsCount),
        Column(w=21, n="# of System", f=lambda x: x.okapiPermissionSetsCount),
        Column(w=21, n="# of Deprecated", f=lambda x: x.deprecatedPermissionSetsCount),
        Column(w=21, n="# of Total", f=lambda x: x.allPermissionSetsCount),
    ]

    def __init__(self, ws: Worksheet, data: List[UserStatistics]):
        super().__init__(ws, self._title, data, self._columns)
        self._data = data

    @override
    def _get_row_fill_color(self, user_stats: UserStatistics) -> Optional[PatternFill]:
        if user_stats.invalidPermissionSetsCount > 0:
            return ws_constants.light_red_fill
        if user_stats.deprecatedPermissionSetsCount > 0:
            return ws_constants.light_yellow_fill
        if user_stats.mutablePermissionSetsCount > 0:
            return ws_constants.light_green_fill
        return ws_constants.almost_white_fill

    def _get_iterable_data(self) -> List[UserStatistics]:
        return sorted(self._data, key=self.__get_sort_order)

    @staticmethod
    def __get_sort_order(user_stats: UserStatistics) -> tuple:
        return (
            -user_stats.mutablePermissionSetsCount,
            -user_stats.invalidPermissionSetsCount,
            -user_stats.okapiPermissionSetsCount,
        )
