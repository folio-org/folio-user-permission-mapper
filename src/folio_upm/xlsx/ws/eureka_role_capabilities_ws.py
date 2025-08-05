from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.eureka.eureka_role_capability import FullRoleCapabilityOrSet
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class RecordRow(BaseModel):
    roleName: str
    capabilityId: str | None = None
    c_type: str
    capabilityType: str
    name: str


class EurekaRoleCapabilitiesWorksheet(AbstractWorksheet):
    title = "Role-Capabilities"

    _columns = [
        Column[RecordRow](w=60, n="Role Name", f=lambda x: x.roleName),
        # Column[RecordRow](w=40, n="Capability ID", f=lambda x: x.capabilityId),
        Column[RecordRow](w=25, n="Resolved Type", f=lambda x: x.c_type),
        Column[RecordRow](w=15, n="Type", f=lambda x: x.capabilityType),
        Column[RecordRow](w=100, n="Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[FullRoleCapabilityOrSet]):
        super().__init__(ws, self.title, data, self._columns)

    @override
    def _get_iterable_data(self) -> List[RecordRow]:
        result = []
        for item in self._data:
            result.append(
                RecordRow(
                    roleName=item.role.name,
                    capabilityId=item.capabilityOrSet.id,
                    c_type=self.__get_c_type(item.capabilityOrSet),
                    capabilityType=item.capabilityOrSet.capabilityType,
                    name=item.capabilityOrSet.name,
                )
            )

        return result

    @staticmethod
    def __get_c_type(item: Capability | CapabilitySet) -> str:
        if isinstance(item, Capability):
            return "capability"
        elif isinstance(item, CapabilitySet):
            return "capability-set"
        else:
            return "unknown"
