from typing import List

from pydantic import BaseModel


class UserRoles(BaseModel):
    userId: str
    roles: List[str] | None = []
