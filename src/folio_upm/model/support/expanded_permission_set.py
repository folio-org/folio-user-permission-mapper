from typing import List

from pydantic import BaseModel


class ExpandedPermissionSet(BaseModel):

    permissionName: str
    expandedFrom: List[str] = []
