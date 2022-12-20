from typing import Union
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel


class Base(BaseModel):
    uuid_: str
    created_at: Union[datetime, str, None] = None
    deleted_at: Union[datetime, str, None] = None
    updated_at: Union[datetime, str, None] = None
    created_by: Union[UUID, str, None] = None
    deleted_by: Union[UUID, str, None] = None
    updated_by: Union[UUID, str, None] = None