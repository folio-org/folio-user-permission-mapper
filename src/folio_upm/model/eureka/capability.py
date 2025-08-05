from typing import List, Optional

from pydantic import BaseModel, Field

from folio_upm.model.eureka.endpoint import Endpoint


class Capability(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    applicationId: str
    moduleId: str
    capabilityType: Optional[str] = Field(alias="type", default=None)
    permission: str
    endpoints: List[Endpoint] = []
    dummyCapability: bool
