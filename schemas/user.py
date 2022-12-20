from typing import Union
from uuid import UUID
from schemas.const import Base
from pydantic import BaseModel, EmailStr, Field


class UserDB(Base):
    profil_user: Union[UUID, str, None] = None
    role: Union[UUID, str, None] = None
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool

class UserAuth(BaseModel):
    email: EmailStr = Field(..., description='User email')
    username: str = Field(..., max_length=50, description="User username")
    password: str = Field(..., max_length=24, description="User password")
    role: Union[str, None] = "warga"
    role: Union[str, None] = "warga"

class UserOut(BaseModel):
    uuid_: str
    username: str
    email: EmailStr
    is_active: Union[bool, None] = False
    role: Union[str, None] = None

class UserUpdate(BaseModel):
    email: Union[EmailStr, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
