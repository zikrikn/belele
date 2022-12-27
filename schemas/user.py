from typing import Union
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserDB(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    hashed_password: str

class UserAuth(BaseModel):
    full_name: str
    email: EmailStr = Field(..., description='User email')
    username: str = Field(..., max_length=50, description="User username")
    password: str = Field(..., max_length=24, description="User password")

class UserOut(BaseModel):
    full_name: str
    username: str
    email: EmailStr
