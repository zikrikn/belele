from pydantic import BaseModel, EmailStr, Field
from typing import Union

class UserDB(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    hashed_password: str
    photoprofile: Union[str, None] = None

class UserAuth(BaseModel):
    full_name: str
    email: EmailStr = Field(..., description='User email')
    username: str = Field(..., max_length=50, description="User username")
    password: str = Field(..., max_length=24, description="User password")

class UserOut(BaseModel):
    full_name: str
    username: str
    email: EmailStr

class ProfileOut(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    photoprofile: Union[str, None] = None
