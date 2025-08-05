from typing import List

from pydantic import BaseModel, field_serializer

from folio_upm.model.eureka.role import Role
from folio_upm.model.support.expanded_permission_set import ExpandedPermissionSet
from folio_upm.utils.ordered_set import OrderedSet


class AnalyzedRole(BaseModel):

    role: Role
    permissionSets: List[ExpandedPermissionSet]
    source: str
    users: OrderedSet[str]
    usersCount: int = 0
    systemGenerated: bool = False
    capabilitiesCount: int = 0
    originalPermissionsCount: int = 0
    expandedPermissionsCount: int = 0

    def get_total_permissions_count(self) -> int:
        return len(self.permissionSets)

    @field_serializer("users")
    def serialize_ordered_set(self, value: OrderedSet[str]) -> List[str]:
        return list(value)
