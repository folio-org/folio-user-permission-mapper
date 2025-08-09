from typing import List

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import num_short_cw, role_name_cw


class CleanHashRoleStatsWorksheet(AbstractWorksheet[FullHashRoleCleanupRecord]):

    _columns = [
        Column[FullHashRoleCleanupRecord](w=role_name_cw, n="Role Name", f=lambda x: x.role.name),
        Column[FullHashRoleCleanupRecord](w=num_short_cw, n="# Capabilities", f=lambda x: len(x.capabilities)),
        Column[FullHashRoleCleanupRecord](w=num_short_cw, n="# Capability Sets", f=lambda x: len(x.capabilitySets)),
    ]

    def __init__(self, ws: Worksheet, data: List[FullHashRoleCleanupRecord]):
        _title = "Hash-Role Stats"
        super().__init__(ws, _title, data, self._columns)
