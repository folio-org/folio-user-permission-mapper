from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.eureka.user_roles import UserRoles
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class EurekaRoleUsersWorksheet(AbstractWorksheet):

    _title = "User-Roles"
    _columns = [
        Column(w=40, n="User Id", f=lambda x: x[0]),
        Column(w=80, n="Role Name", f=lambda x: x[1]),
    ]

    def __init__(self, ws: Worksheet, data: List[UserRoles]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_iterable_data(self):
        return [(user_roles.userId, role_name) for user_roles in self._data for role_name in user_roles.roles]
