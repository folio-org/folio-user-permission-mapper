from typing import List

from pydantic import BaseModel

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.eureka.role import Role


class FullHashRoleCleanupRecord(BaseModel):
    role: Role
    capabilities: List[Capability]
    capabilitySets: List[CapabilitySet]
