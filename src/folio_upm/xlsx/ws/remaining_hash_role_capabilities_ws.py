from typing import List, Any

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.xlsx.abstract_ws import AbstractWorksheet


class RemainingHashRoleCapabilitiesWorksheet(AbstractWorksheet):

    _title = "Remaining Hash-Role Capabilities"
    _columns = [

    ]

    def __init__(self, ws: Worksheet, data: List[Any]):
        super().__init__(ws, self._title, data, self._columns)
