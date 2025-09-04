from typing import List, Tuple

from pydantic import BaseModel


class UserPermsHolder(BaseModel):
    mutablePermissions: List[str] = []
    systemPermissions: List[Tuple[str, bool, bool]] = []
