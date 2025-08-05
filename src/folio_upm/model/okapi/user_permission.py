from typing import List

from pydantic import BaseModel


class UserPermission(BaseModel):
    id: str
    userId: str
    permissions: List[str] = []
