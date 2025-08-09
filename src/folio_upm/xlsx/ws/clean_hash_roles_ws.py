from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import desc_long_cw, role_name_cw, type_cw


class RoleCapabilityRow(BaseModel):
    roleName: str
    c_type: str
    capabilityType: str
    name: str


class CleanHashRolesWorksheet(AbstractWorksheet[RoleCapabilityRow]):

    _columns = [
        Column[RoleCapabilityRow](w=role_name_cw, n="Role Name", f=lambda x: x.roleName),
        Column[RoleCapabilityRow](w=type_cw, n="Resolved Type", f=lambda x: x.c_type),
        Column[RoleCapabilityRow](w=type_cw, n="Type", f=lambda x: x.capabilityType),
        Column[RoleCapabilityRow](w=desc_long_cw, n="Capability | Set Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[FullHashRoleCleanupRecord]):
        _title = "Clean Hash-Roles"
        super().__init__(ws, _title, data, self._columns)

    @override
    def _get_iterable_data(self) -> List[RoleCapabilityRow]:
        result = []
        for item in self._data:
            role_name = item.role.name
            if len(item.capabilities) == 0 and len(item.capabilitySets) == 0:
                row = RoleCapabilityRow(roleName=role_name, c_type="none", capabilityType="none", name="none")
                result.append(row)
                continue

            for capability in item.capabilities:
                row = RoleCapabilityRow(
                    roleName=role_name,
                    c_type="capability",
                    capabilityType=capability.capabilityType,
                    name=capability.name,
                )
                result.append(row)

            for capability_set in item.capabilitySets:
                row = RoleCapabilityRow(
                    roleName=role_name,
                    c_type="capability-set",
                    capabilityType=capability_set.capabilityType,
                    name=capability_set.name,
                )
                result.append(row)

        return result
