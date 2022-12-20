from uuid import UUID
from typing import Union
from datetime import date

from pydantic import BaseModel
from .const import Base


class ProfilDB(Base):
    id_user: Union[UUID, str]
    penyakit: Union[UUID, None] = None
    nama_lengkap: Union[str, None] = None
    kota_lahir: Union[str, None] = None
    tanggal_lahir: Union[date, None] = None

class ProfilIn(BaseModel):
    penyakit: Union[UUID, str, None] = None
    nama_lengkap: Union[str, None] = None
    kota_lahir: Union[str, None] = None
    tanggal_lahir: Union[date, str, None] = None
