from typing import List, Optional

from pydantic import BaseModel


class RoleUsers(BaseModel):
    roleName: Optional[str]
    userIds: List[str]
