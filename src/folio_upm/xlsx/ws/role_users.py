from typing import List, Optional, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.dto.eureka import RoleUsers
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class UserRoleRow(BaseModel):
    name: Optional[str]
    id: str
    userId: str


class RoleUsersWorksheet(AbstractWorksheet):
    _title = "Role-Users"
    _columns = [
        Column(w=40, n="Role Id", f=lambda x: x.id),
        Column(w=80, n="Role Name", f=lambda x: x.name),
        Column(w=40, n="User Id", f=lambda x: x.userId),
    ]

    def __init__(self, ws: Worksheet, data: List[RoleUsers]):
        super().__init__(ws, self._title, data, self._columns)
        self._yellow_types = ["deprecated", "questionable", "unprocessed"]

    @override
    def _get_iterable_data(self):
        return [
            UserRoleRow(userId=user_id, id=role_users.roleId, name=role_users.roleName)
            for role_users in self._data
            for user_id in role_users.userIds
        ]
