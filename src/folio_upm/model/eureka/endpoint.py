from pydantic import BaseModel


class Endpoint(BaseModel):
    path: str
    method: str
