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
    permissionType: Optional[str]
    displayName: Optional[str] = None
    expandedFrom: Optional[str] = None
    name: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    capabilityType: Optional[str] = None


class RoleCapabilitiesHolder(BaseModel):
    roleName: str
    capabilities: List[CapabilityPlaceholder]


class SourcedPermissionSet(BaseModel):
    src: SourceType
    val: PermissionSet


class ExpandedPermissionSet(BaseModel):
    permissionName: str
    expandedFrom: Optional[str] = None


class AnalyzedPermissionSet(BaseModel):
    note: Optional[str] = None
    reasons: List[str] = []
    permissionName: str = None
    sourcePermSets: List[SourcedPermissionSet] = []

    def get_first_value(self, value_extractor: Callable[[PermissionSet], str]) -> Optional[str]:
        extracted_values = [value_extractor(i.val) for i in self.sourcePermSets]
        return extracted_values[0] if len(extracted_values) > 1 else None

    def get_parent_permission_names(self) -> OrderedSet[str]:
        parent_permissions = OrderedSet[str]()
        for source_perm_set in self.sourcePermSets:
            if source_perm_set.val.childOf:
                parent_permissions.add_all(source_perm_set.val.childOf)
        return parent_permissions

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
