from typing import List

from pydantic import BaseModel

from folio_upm.model.okapi.permission_set import PermissionSet


class ModuleDescriptor(BaseModel):

    id: str
    name: str = None
    description: str = None
    permissionSets: List[PermissionSet] = []
