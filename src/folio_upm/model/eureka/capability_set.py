from typing import List, Optional

from pydantic import BaseModel, Field


class CapabilitySet(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    applicationId: Optional[str] = None
    moduleId: Optional[str] = None
    capabilityType: Optional[str] = Field(alias="type", default=None)
    permission: str
    capabilities: List[str] = []
