from typing import List, Optional

from pydantic import BaseModel

from folio_upm.model.types.permission_type import PermissionType


class AnalyzedCapability(BaseModel):
    resolvedType: str
    permissionName: str
    permissionType: Optional[str] = None
    displayName: Optional[str] = None
    expandedFrom: List[str] = []
    name: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    capabilityType: Optional[str] = None

    def get_permission_type_name(self) -> str:
        return PermissionType.from_string(self.permissionType).get_visible_name()
