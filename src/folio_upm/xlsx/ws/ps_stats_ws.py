from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.permission_type import DEPRECATED, INVALID, MUTABLE, QUESTIONABLE, UNPROCESSED, PermissionType
from folio_upm.dto.results import PsStatistics
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class PermissionStatsWorksheet(AbstractWorksheet):

    title = "PS-Stats-Okapi"

    _columns = [
        Column[PsStatistics](w=80, n="PS Name", f=lambda x: x.name),
        Column[PsStatistics](w=100, n="Display Name", f=lambda x: x.get_uq_display_names_str()),
        Column[PsStatistics](w=18, n="PS Type", f=lambda x: x.get_permission_type_name()),
        Column[PsStatistics](w=16, n="# Parent PS", f=lambda x: x.parentPermsCount),
        Column[PsStatistics](w=16, n="# Sub PS", f=lambda x: x.subPermsCount),
        Column[PsStatistics](w=23, n="# Flat Sub PS", f=lambda x: x.flatPermCount),
        Column[PsStatistics](w=60, n="Modules", f=lambda x: x.get_uq_modules_str()),
        Column[PsStatistics](w=20, n="Found In", f=lambda x: x.get_uq_sources_str()),
        Column[PsStatistics](w=25, n="# Definitions", f=lambda x: x.refCount),
        Column[PsStatistics](w=30, n="Note", f=lambda x: x.note),
        Column[PsStatistics](w=35, n="Invalidity Reason", f=lambda x: x.get_reasons_str()),
    ]

    def __init__(self, ws: Worksheet, data: List[PsStatistics]):
        super().__init__(ws, self.title, data, self._columns)
        self._yellow_types = [x.get_name() for x in [DEPRECATED, QUESTIONABLE, UNPROCESSED]]

    @override
    def _get_row_fill_color(self, ps_stats: PsStatistics) -> Optional[PatternFill]:
        ps_type = PermissionType.from_string(ps_stats.permissionType)
        if ps_stats.refCount > ps_stats.get_uq_sources_num() or ps_type == INVALID:
            return ws_constants.light_red_fill
        if ps_type == MUTABLE:
            return ws_constants.light_green_fill
        if ps_type in self._yellow_types:
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill
