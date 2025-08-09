from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.model.eureka.user_roles import UserRoles
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import desc_long_cw, uuid_cw


class UserRoleRow(BaseModel):
    name: str
    userId: str


class UserRolesWorksheet(AbstractWorksheet):
    _title = "User-Roles"
    _columns = [
        Column[UserRoleRow](w=uuid_cw, n="User Id", f=lambda x: x.userId),
        Column[UserRoleRow](w=desc_long_cw, n="Role Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[UserRoles]):
        super().__init__(ws, self._title, data, self._columns)
        self._yellow_types = ["deprecated", "questionable", "unprocessed"]

    @override
    def _get_iterable_data(self) -> List[UserRoleRow]:
        return [
            UserRoleRow(userId=user_roles.userId, name=role_name)
            for user_roles in self._data
            for role_name in user_roles.roleNames
        ]
