from typing import Optional

from pydantic import BaseModel


class Role(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
