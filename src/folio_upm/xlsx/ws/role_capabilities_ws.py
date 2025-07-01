from typing import Optional
from typing import OrderedDict as OrdDict
from typing import override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.dto.permission_type import INVALID, MUTABLE, DEPRECATED, QUESTIONABLE, UNPROCESSED
from folio_upm.dto.support import RoleCapabilitiesHolder
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column


class RoleCapabilityRow(BaseModel):
    roleName: str
    source: str
    excluded: bool
    expandedFrom: Optional[str] = None
    sourceDisplayName: Optional[str]
    sourceType: Optional[str]
    resolvedType: Optional[str]
    name: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    capabilityType: Optional[str]


class RolesCapabilitiesWorksheet(AbstractWorksheet):

    _title = "Role-Capabilities"
    _columns = [
        Column[RoleCapabilityRow](w=60, n="Role Name", f=lambda x: x.roleName),
        Column[RoleCapabilityRow](w=80, n="PS Name", f=lambda x: x.source),
        Column[RoleCapabilityRow](w=80, n="PS Display Name", f=lambda x: x.sourceDisplayName),
        Column[RoleCapabilityRow](w=18, n="PS Type", f=lambda x: x.sourceType),
        Column[RoleCapabilityRow](w=80, n="Expanded From", f=lambda x: x.expandedFrom),
        Column[RoleCapabilityRow](w=20, n="Map Target", f=lambda x: x.resolvedType),
        Column[RoleCapabilityRow](w=60, n="Capability Name", f=lambda x: x.name),
        Column[RoleCapabilityRow](w=60, n="Capability Resource", f=lambda x: x.resource),
        Column[RoleCapabilityRow](w=60, n="Capability Action", f=lambda x: x.action),
        Column[RoleCapabilityRow](w=22, n="Capability Type", f=lambda x: x.capabilityType),
    ]

    def __init__(self, ws: Worksheet, data: OrdDict[str, RoleCapabilitiesHolder]):
        super().__init__(ws, self._title, data, self._columns)

        self._red_types = [INVALID, MUTABLE]
        self._yellow_types = [DEPRECATED, QUESTIONABLE, UNPROCESSED]

    @override
    def _get_iterable_data(self):
        return [
            RoleCapabilityRow(
                roleName=role_capability.roleName,
                resolvedType=capability.resolvedType,
                source=capability.permissionName,
                sourceDisplayName=capability.displayName,
                sourceType=capability.permissionType,
                name=capability.name,
                resource=capability.resource,
                action=capability.action,
                expandedFrom=capability.expandedFrom,
                excluded=False,
                capabilityType=capability.capabilityType,
            )
            for role_capability in self._data
            for capability in role_capability.capabilities
        ]

    @override
    def _get_row_fill_color(self, value: RoleCapabilityRow) -> Optional[PatternFill]:
        if value.sourceType in self._red_types or value.sourceType is None:
            return ws_constants.light_red_fill
        if value.excluded or (value.sourceType in self._yellow_types) or value.resolvedType == "not_found":
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill
