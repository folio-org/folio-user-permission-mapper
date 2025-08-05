from typing import List

from pydantic import BaseModel


class UserCapabilities(BaseModel):
    allCapabilities: List[str] = []
    allCapabilitySets: List[str] = []
    roleCapabilities: List[str] = []
    roleCapabilitySets: List[str] = []
    hashRoleCapabilities: List[str] = []
    hashRoleCapabilitySets: List[str] = []
