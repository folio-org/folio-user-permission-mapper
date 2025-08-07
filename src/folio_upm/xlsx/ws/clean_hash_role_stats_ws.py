from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class CleanHashRoleStatsWorksheet(AbstractWorksheet):

    _title = "Hash-Role Stats"
    _columns = [
        Column[FullHashRoleCleanupRecord](w=80, n="Role Name", f=lambda x: x.role.name),
        Column[FullHashRoleCleanupRecord](w=25, n="# Capabilities", f=lambda x: len(x.capabilities)),
        Column[FullHashRoleCleanupRecord](w=25, n="# Capability Sets", f=lambda x: len(x.capabilitySets)),
    ]

    def __init__(self, ws: Worksheet, data: List[FullHashRoleCleanupRecord]):
        super().__init__(ws, self._title, data, self._columns)
