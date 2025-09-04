from typing import List

from pydantic import BaseModel

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.eureka.role import Role
from folio_upm.model.eureka.role_capability import RoleCapability
from folio_upm.model.eureka.role_capability_set import RoleCapabilitySet
from folio_upm.model.eureka.user_role import UserRole


class EurekaLoadResult(BaseModel):
    roles: List[Role] = []
    roleCapabilities: List[RoleCapability] = []
    roleCapabilitySets: List[RoleCapabilitySet] = []
    roleUsers: List[UserRole] = []
    capabilities: List[Capability] = []
    capabilitySets: List[CapabilitySet] = []
