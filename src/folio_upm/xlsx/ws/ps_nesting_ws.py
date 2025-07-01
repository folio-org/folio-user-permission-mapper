from typing import List, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.permission_type import INVALID
from folio_upm.dto.results import AnalyzedParentPermSets
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class PermissionNestingWorksheet(AbstractWorksheet):
    _title = "PS Nesting"
    _columns = [
        Column[AnalyzedParentPermSets](w=80, n="PS", f=lambda x: x.permissionName),
        Column[AnalyzedParentPermSets](w=80, n="PS Name", f=lambda x: x.displayName),
        Column[AnalyzedParentPermSets](w=18, n="PS Type", f=lambda x: x.get_permission_type_name()),
        Column[AnalyzedParentPermSets](w=80, n="Parent PS", f=lambda x: x.parentPermissionName),
        Column[AnalyzedParentPermSets](w=80, n="Parent Name", f=lambda x: x.parentDisplayName),
        Column[AnalyzedParentPermSets](w=18, n="Parent Types", f=lambda x: x.get_parent_types_str()),
        # Column[AnalyzedParentPermSets](w=18, n="Parent Sources", f=lambda x: x.get_parent_sources_str()),
    ]

    def __init__(self, ws: Worksheet, data: List[AnalyzedParentPermSets]):
        super().__init__(ws, self._title, data, self._columns)
        self._yellow_types = ["deprecated", "questionable", "unprocessed"]

    @override
    def _get_row_fill_color(self, value: AnalyzedParentPermSets) -> Optional[PatternFill]:
        if len(value.parentPsTypes) == 0 or INVALID.get_name() in value.parentPsTypes:
            return ws_constants.light_red_fill
        if True in [x in value.parentPsTypes for x in self._yellow_types]:
            return ws_constants.light_yellow_fill
        if "mutable" in value.parentPsTypes:
            return ws_constants.light_green_fill
        return ws_constants.almost_white_fill
