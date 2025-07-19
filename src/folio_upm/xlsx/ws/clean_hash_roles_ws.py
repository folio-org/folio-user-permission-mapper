from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.dto.cleanup import CleanHashRole
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class CleanHashRoleRow(BaseModel):
    roleName: str
    c_type: str
    capabilityType: str
    name: str


class CleanHashRolesWorksheet(AbstractWorksheet):

    _title = "Clean Hash-Roles"
    _columns = [
        Column[CleanHashRoleRow](w=60, n="Role Name", f=lambda x: x.roleName),
        Column[CleanHashRoleRow](w=25, n="Resolved Type", f=lambda x: x.c_type),
        Column[CleanHashRoleRow](w=15, n="Type", f=lambda x: x.capabilityType),
        Column[CleanHashRoleRow](w=100, n="Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[CleanHashRole]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_iterable_data(self) -> List[CleanHashRoleRow]:
        result = []
        for item in self._data:
            role_name = item.role.name
            if len(item.capabilities) == 0 and len(item.capabilitySets) == 0:
                row = CleanHashRoleRow(roleName=role_name, c_type="none", capabilityType="none", name="none")
                result.append(row)
                continue

            for capability in item.capabilities:
                row = CleanHashRoleRow(
                    roleName=role_name,
                    c_type="capability",
                    capabilityType=capability.capabilityType,
                    name=capability.name,
                )
                result.append(row)

            for capability_set in item.capabilitySets:
                row = CleanHashRoleRow(
                    roleName=role_name,
                    c_type="capability-set",
                    capabilityType=capability_set.capabilityType,
                    name=capability_set.name,
                )
                result.append(row)

        return result
