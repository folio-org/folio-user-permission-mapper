from typing import Union

from pydantic import BaseModel

from folio_upm.model.eureka.capability import Capability
from folio_upm.model.eureka.capability_set import CapabilitySet
from folio_upm.model.eureka.role import Role


class RoleCapabilityOrSet(BaseModel):
    role: Role
    capabilityOrSet: Union[Capability, CapabilitySet, None]
