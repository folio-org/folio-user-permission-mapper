from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.model.eureka.user_roles import UserRoles
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class CleanHashRoleStatsWorksheet(AbstractWorksheet):

    _title = "User-Roles"
    _columns = [
        Column[FullHashRoleCleanupRecord](w=40, n="Role Name", f=lambda x: x.role.name),
        Column[FullHashRoleCleanupRecord](w=25, n="# Capabilities", f=lambda x: len(x.capabilities)),
        Column[FullHashRoleCleanupRecord](w=25, n="# Capability Sets", f=lambda x: len(x.capabilitySets)),
    ]

    def __init__(self, ws: Worksheet, data: List[FullHashRoleCleanupRecord]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_iterable_data(self):
        return [(user_roles.userId, role_name) for user_roles in self._data for role_name in user_roles.roles]
