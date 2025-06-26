from typing import Callable, List, Optional, Tuple

from pydantic import BaseModel

from folio_upm.dto.okapi import PermissionSet
from folio_upm.dto.source_type import SourceType
from folio_upm.utils.ordered_set import OrderedSet


class UserPermsHolder(BaseModel):
    mutablePermissions: List[str] = []
    systemPermissions: List[Tuple[str, bool, bool]] = []


class CapabilityPlaceholder(BaseModel):
    resolvedType: str
    permissionName: str
    permissionType: str
    displayName: Optional[str]
    expandedFrom: Optional[str]
    name: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    capabilityType: Optional[str]


class RoleCapabilitiesHolder(BaseModel):
    roleId: str
    roleName: str
    capabilities: List[CapabilityPlaceholder]


class SourcedPermissionSet(BaseModel):
    src: SourceType
    val: PermissionSet


class ExpandedPermissionSet(BaseModel):
    permissionName: str
    expandedFrom: Optional[str]


class AnalyzedPermissionSet(BaseModel):
    note: Optional[str] = None
    reasons: List[str] = []
    permissionName: str = None
    sourcePermSets: List[SourcedPermissionSet] = []

    def get_first_value(self, value_extractor: Callable[[PermissionSet], str]) -> Optional[str]:
        extracted_values = [value_extractor(i.val) for i in self.sourcePermSets]
        return extracted_values[0] if len(extracted_values) > 1 else None

    def get_sub_permissions(self, include_flat: bool = False) -> OrderedSet[str]:
        sub_permissions = OrderedSet()
        for source_perm_set in self.sourcePermSets:
            if not include_flat and source_perm_set.src == SourceType.FLAT_PS:
                continue
            sub_permissions += source_perm_set.val.subPermissions
        return sub_permissions

    def get_uq_display_names_str(self) -> str:
        names = OrderedSet[str]([x.val.displayName for x in self.sourcePermSets if x.val.displayName]).to_list()
        return "\n".join(sorted(names))
