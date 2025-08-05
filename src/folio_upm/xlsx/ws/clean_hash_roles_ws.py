from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.model.cleanup.full_hash_role_cleanup_record import FullHashRoleCleanupRecord
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class RecordRow(BaseModel):
    roleName: str
    c_type: str
    capabilityType: str
    name: str


class CleanHashRolesWorksheet(AbstractWorksheet):

    _title = "Clean Hash-Roles"
    _columns = [
        Column[RecordRow](w=60, n="Role Name", f=lambda x: x.roleName),
        Column[RecordRow](w=25, n="Resolved Type", f=lambda x: x.c_type),
        Column[RecordRow](w=15, n="Type", f=lambda x: x.capabilityType),
        Column[RecordRow](w=100, n="Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[FullHashRoleCleanupRecord]):
        super().__init__(ws, self._title, data, self._columns)

    @override
    def _get_iterable_data(self) -> List[RecordRow]:
        result = []
        for item in self._data:
            role_name = item.role.name
            if len(item.capabilities) == 0 and len(item.capabilitySets) == 0:
                row = RecordRow(roleName=role_name, c_type="none", capabilityType="none", name="none")
                result.append(row)
                continue

            for capability in item.capabilities:
                row = RecordRow(
                    roleName=role_name,
                    c_type="capability",
                    capabilityType=capability.capabilityType,
                    name=capability.name,
                )
                result.append(row)

            for capability_set in item.capabilitySets:
                row = RecordRow(
                    roleName=role_name,
                    c_type="capability-set",
                    capabilityType=capability_set.capabilityType,
                    name=capability_set.name,
                )
                result.append(row)

        return result
