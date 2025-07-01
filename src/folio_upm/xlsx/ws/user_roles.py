from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.dto.eureka import RoleUsers
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class UserRoleRow(BaseModel):
    name: str
    userId: str


class UserRolesWorksheet(AbstractWorksheet):
    _title = "Role-Users"
    _columns = [
        Column(w=40, n="User Id", f=lambda x: x.userId),
        Column(w=80, n="Role Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[RoleUsers]):
        super().__init__(ws, self._title, data, self._columns)
        self._yellow_types = ["deprecated", "questionable", "unprocessed"]

    @override
    def _get_iterable_data(self):
        return [
            UserRoleRow(userId=user_roles.userId, name=role_name)
            for user_roles in self._data
            for role_name in user_roles.roles
        ]
