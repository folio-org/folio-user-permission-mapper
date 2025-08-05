from pydantic import BaseModel


class RoleCapability(BaseModel):
    roleId: str
    capabilityId: str
