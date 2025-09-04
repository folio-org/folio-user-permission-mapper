from typing import List, Optional

from pydantic import BaseModel

from folio_upm.model.okapi.permission_set import PermissionSet


class ModuleDescriptor(BaseModel):

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    permissionSets: List[PermissionSet] = []
