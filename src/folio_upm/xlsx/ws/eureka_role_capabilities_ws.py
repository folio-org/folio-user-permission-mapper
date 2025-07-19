from typing import List

from openpyxl.worksheet.worksheet import Worksheet

from folio_upm.dto.cleanup import EurekaRoleCapability
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class EurekaRoleCapabilitiesWorksheet(AbstractWorksheet):
    title = "Role-Capabilities"

    _columns = [
        Column[EurekaRoleCapability](w=60, n="Role Name", f=lambda x: x.roleName),
        # Column[EurekaRoleCapability](w=40, n="Capability ID", f=lambda x: x.capabilityId),
        Column[EurekaRoleCapability](w=25, n="Resolved Type", f=lambda x: x.c_type),
        Column[EurekaRoleCapability](w=15, n="Type", f=lambda x: x.capabilityType),
        Column[EurekaRoleCapability](w=100, n="Name", f=lambda x: x.name),
    ]

    def __init__(self, ws: Worksheet, data: List[EurekaRoleCapability]):
        super().__init__(ws, self.title, data, self._columns)
