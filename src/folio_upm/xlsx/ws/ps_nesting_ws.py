from typing import List, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.analysis.analyzed_parent_permission_set import AnalyzedParentPermSets
from folio_upm.model.types.permission_type import INVALID, MUTABLE
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import ps_name_cw, type_cw


class PermissionNestingWorksheet(AbstractWorksheet[AnalyzedParentPermSets]):
    _title = "PS Nesting"
    _columns = [
        Column[AnalyzedParentPermSets](w=ps_name_cw, n="PS", f=lambda x: x.permissionName),
        Column[AnalyzedParentPermSets](w=ps_name_cw, n="PS Name", f=lambda x: x.displayName),
        Column[AnalyzedParentPermSets](w=type_cw, n="PS Type", f=lambda x: x.get_permission_type_name()),
        Column[AnalyzedParentPermSets](w=ps_name_cw, n="Parent PS", f=lambda x: x.parentPermissionName),
        Column[AnalyzedParentPermSets](w=ps_name_cw, n="Parent Name", f=lambda x: x.parentDisplayName),
        Column[AnalyzedParentPermSets](w=type_cw, n="Parent Types", f=lambda x: x.get_parent_types_str()),
    ]

    def __init__(self, ws: Worksheet, data: List[AnalyzedParentPermSets]):
        super().__init__(ws, self._title, data, self._columns)
        self._yellow_types = ["deprecated", "questionable", "unprocessed"]

    @override
    def _get_row_fill_color(self, value: AnalyzedParentPermSets) -> PatternFill:
        if len(value.parentPsTypes) == 0 or INVALID.get_name() in value.parentPsTypes:
            return ws_constants.light_red_fill
        if True in [x in value.parentPsTypes for x in self._yellow_types]:
            return ws_constants.light_yellow_fill
        if MUTABLE.get_name() in value.parentPsTypes:
            return ws_constants.light_green_fill
        return ws_constants.almost_white_fill
