from pydantic import BaseModel


class DetailedHttpError(BaseModel):
    message: str
    status: int = 500
    responseBody: str = ""
