from typing import List, Optional

from pydantic import BaseModel, Field


class CapabilitySet(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    applicationId: str
    moduleId: str
    capabilityType: Optional[str] = Field(alias="type", default=None)
    permission: str
    capabilities: Optional[List[str]] = []
