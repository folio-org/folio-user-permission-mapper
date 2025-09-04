from typing import List

from pydantic import BaseModel


class ExtraPermissionSetData(BaseModel):
    viewPermissions: List[str] = []
    editPermissions: List[str] = []
    viewCapabilities: List[str] = []
    editCapabilities: List[str] = []
