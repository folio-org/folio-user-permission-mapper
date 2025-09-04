from typing import List, override

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.eureka.role_capability_or_set import RoleCapabilityOrSet
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import desc_long_cw, role_name_cw, type_cw


class RoleCapabilityRow(BaseModel):
    roleName: str
    capabilityId: str | None = None
    c_type: str
    capabilityType: str
    name: str


class EurekaRoleCapabilitiesWorksheet(AbstractWorksheet[RoleCapabilityRow]):

    _columns = [
        Column[RoleCapabilityRow](w=role_name_cw, n="Role Name", f=lambda x: x.roleName),
        Column[RoleCapabilityRow](w=type_cw, n="Resolved Type", f=lambda x: x.c_type),
        Column[RoleCapabilityRow](w=type_cw, n="Type", f=lambda x: x.capabilityType),
        Column[RoleCapabilityRow](w=desc_long_cw, n="Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[RoleCapabilityOrSet]):
        title = "Role-Capabilities"
        super().__init__(ws, title, data, self._columns)

    @override
    def _get_iterable_data(self) -> List[RoleCapabilityRow]:
        result = []
        for item in self._data:
            result.append(
                RoleCapabilityRow(
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
