from typing import Union, Any
from typing import Union, Any
from uuid import UUID
from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

class TokenPayLoad(BaseModel):
    sub: Union[Union[UUID, Any], Any] = None
    exp: int = None