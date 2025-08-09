from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.model.eureka.user_roles import UserRoles
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import role_name_cw, uuid_cw


class EurekaRoleUsersWorksheet(AbstractWorksheet):

    _columns = [
        Column(w=uuid_cw, n="User Id", f=lambda x: x[0]),
        Column(w=role_name_cw, n="Role Name", f=lambda x: x[1]),
    ]

    def __init__(self, ws: Worksheet, data: List[UserRoles]):
        _title = "User-Roles"
        super().__init__(ws, _title, data, self._columns)

    @override
    def _get_iterable_data(self):
        return [(user_roles.userId, role_name) for user_roles in self._data for role_name in user_roles.roles]
