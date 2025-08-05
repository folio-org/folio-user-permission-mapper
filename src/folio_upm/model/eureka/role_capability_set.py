from pydantic import BaseModel


class RoleCapabilitySet(BaseModel):
    roleId: str
    capabilitySetId: str
