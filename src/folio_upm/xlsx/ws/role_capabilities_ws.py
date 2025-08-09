from typing import Dict, Optional, override

from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet
from pydantic import BaseModel

from folio_upm.model.analysis.analyzed_role_capabilities import AnalyzedRoleCapabilities
from folio_upm.model.types.permission_type import DEPRECATED, INVALID, MUTABLE, QUESTIONABLE, UNPROCESSED
from folio_upm.xlsx import ws_constants
from folio_upm.xlsx.abstract_ws import AbstractWorksheet, Column
from folio_upm.xlsx.ws_constants import bool_cw_short, desc_med_cw, desc_short_cw, ps_name_cw, role_name_cw, type_cw


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


class RolesCapabilitiesWorksheet(AbstractWorksheet[RoleCapabilityRow]):

    _title = "Role-Capabilities"
    _columns = [
        Column[RoleCapabilityRow](w=role_name_cw, n="Role Name", f=lambda x: x.roleName),
        Column[RoleCapabilityRow](w=ps_name_cw, n="PS Name", f=lambda x: x.source),
        Column[RoleCapabilityRow](w=ps_name_cw, n="PS Display Name", f=lambda x: x.sourceDisplayName),
        Column[RoleCapabilityRow](w=bool_cw_short, n="Match Status", f=lambda x: x.resolvedType),
        Column[RoleCapabilityRow](w=type_cw, n="PS Type", f=lambda x: x.sourceType),
        Column[RoleCapabilityRow](w=ps_name_cw, n="Expanded From", f=lambda x: x.expandedFrom),
        Column[RoleCapabilityRow](w=desc_med_cw, n="Capability Name", f=lambda x: x.name),
        Column[RoleCapabilityRow](w=desc_short_cw, n="Capability Resource", f=lambda x: x.resource),
        Column[RoleCapabilityRow](w=type_cw, n="Capability Action", f=lambda x: x.action),
        Column[RoleCapabilityRow](w=type_cw, n="Capability Type", f=lambda x: x.capabilityType),
    ]

    def __init__(self, ws: Worksheet, data: Dict[str, AnalyzedRoleCapabilities]):
        super().__init__(ws, self._title, data, self._columns)

        self._red_types = [INVALID, MUTABLE]
        self._yellow_types = [DEPRECATED, QUESTIONABLE, UNPROCESSED]

    @override
    def _get_iterable_data(self) -> list[RoleCapabilityRow]:
        return [
            RoleCapabilityRow(
                roleName=role_capability.roleName,
                resolvedType=capability.resolvedType,
                source=capability.permissionName,
                sourceDisplayName=capability.displayName,
                sourceType=capability.get_permission_type_name(),
                name=capability.name,
                resource=capability.resource,
                action=capability.action,
                expandedFrom=", ".join(capability.expandedFrom),
                excluded=False,
                capabilityType=capability.capabilityType,
            )
            for role_capability in self._data
            for capability in role_capability.capabilities
        ]

    @override
    def _get_row_fill_color(self, value: RoleCapabilityRow) -> PatternFill:
        if value.sourceType in self._red_types or value.sourceType is None:
            return ws_constants.light_red_fill
        if value.excluded or (value.sourceType in self._yellow_types) or value.resolvedType == "not_found":
            return ws_constants.light_yellow_fill
        return ws_constants.almost_white_fill
