from typing import List, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.stats.permission_set_stats import PermissionSetStats
from folio_upm.model.types.permission_type import (
    DEPRECATED,
    INVALID,
    MUTABLE,
    QUESTIONABLE,
    UNPROCESSED,
    PermissionType,
)
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import desc_med_cw, desc_short_cw, note_cw, num_short_cw, ps_name_cw, type_cw


class PermissionStatsWorksheet(AbstractWorksheet[PermissionSetStats]):

    _columns = [
        Column[PermissionSetStats](w=ps_name_cw, n="PS Name", f=lambda x: x.name),
        Column[PermissionSetStats](w=desc_med_cw, n="Display Name", f=lambda x: x.get_uq_display_names_str()),
        Column[PermissionSetStats](w=type_cw, n="PS Type", f=lambda x: x.get_permission_type_name()),
        Column[PermissionSetStats](w=num_short_cw, n="# Parent PS", f=lambda x: x.parentPermsCount),
        Column[PermissionSetStats](w=num_short_cw, n="# Sub PS", f=lambda x: x.subPermsCount),
        Column[PermissionSetStats](w=num_short_cw, n="# Flat Sub PS", f=lambda x: x.flatPermCount),
        Column[PermissionSetStats](w=desc_short_cw, n="Modules", f=lambda x: x.get_uq_modules_str()),
        Column[PermissionSetStats](w=type_cw, n="Found In", f=lambda x: x.get_uq_sources_str()),
        Column[PermissionSetStats](w=num_short_cw, n="# Definitions", f=lambda x: x.refCount),
        Column[PermissionSetStats](w=note_cw, n="Note", f=lambda x: x.note),
        Column[PermissionSetStats](w=note_cw, n="Invalidity Reason", f=lambda x: x.get_reasons_str()),
    ]

    def __init__(self, ws: Worksheet, data: List[PermissionSetStats]):
        title = "PS-Stats-Okapi"
        super().__init__(ws, title, data, self._columns)
        self._yellow_types = [x.get_name() for x in [DEPRECATED, QUESTIONABLE, UNPROCESSED]]

    @override
    def _get_row_fill_color(self, value: PermissionSetStats) -> PatternFill:
        ps_type = PermissionType.from_string(value.permissionType)
        if value.refCount > value.get_uq_sources_num() or ps_type == INVALID:
            return ws_constants.light_red_fill
        if ps_type == MUTABLE:
            return ws_constants.light_green_fill
        if ps_type in self._yellow_types:
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill
