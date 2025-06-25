from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.results import PsStatistics
from folio_upm.xlsx import constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class PermissionStatsWorksheet(AbstractWorksheet):

    title = "PS Stats"
    _yellow_types = ["deprecated", "questionable", "unprocessed"]
    _columns = [
        Column[PsStatistics](w=80, n="PS Name", f=lambda x: x.name),
        Column[PsStatistics](w=100, n="Display Name", f=lambda x: x.get_uq_display_names_str()),
        Column[PsStatistics](w=15, n="PS Type", f=lambda x: x.type),
        Column[PsStatistics](w=16, n="# of Parent", f=lambda x: x.parentPermsCount),
        Column[PsStatistics](w=16, n="# of Sub PS", f=lambda x: x.subPermsCount),
        Column[PsStatistics](w=23, n="# of Flat Sub PS", f=lambda x: x.flatPermCount),
        Column[PsStatistics](w=20, n="Found In", f=lambda x: x.get_uq_sources_str()),
        Column[PsStatistics](w=60, n="Modules", f=lambda x: x.get_uq_modules_str()),
        Column[PsStatistics](w=25, n="# of Definitions", f=lambda x: x.refCount),
        Column[PsStatistics](w=30, n="Note", f=lambda x: x.note),
        Column[PsStatistics](w=35, n="Invalidity Reason", f=lambda x: x.get_reasons_str()),
    ]

    def __init__(self, ws: Worksheet, data: List[PsStatistics]):
        super().__init__(ws, self.title, data, self._columns)
        self._data = data

    @override
    def _get_row_fill_color(self, ps_stats: PsStatistics) -> Optional[PatternFill]:
        if ps_stats.refCount > ps_stats.get_uq_sources_num() or ps_stats.type == "invalid":
            return constants.light_red_fill
        if ps_stats.type == "mutable":
            return constants.light_green_fill
        if ps_stats.type in self._yellow_types:
            return constants.light_yellow_fill
        return constants.almost_white_fill
