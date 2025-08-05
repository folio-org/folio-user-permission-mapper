from pydantic import BaseModel


class UserRole(BaseModel):
    userId: str
    roleId: str
