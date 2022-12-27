from pydantic import BaseModel
from typing import Union
from datetime import datetime, date, timedelta
from schemas.const import Base

class inputNotifikasi(Base):
    key: str #Notifikasi.ID
    tipe: str
    waktu: Union[str, None] = None
    waktu_masuk: Union[datetime, date, timedelta, str, None] = None
    waktu_keluar: Union[datetime, date, timedelta, str, None] = None
    waktu_habis: Union[datetime, date, timedelta, str, None] = None

class outputNotifikasi(Base):
    key: str #Notifikasi.ID
    tipe: str
    waktu: Union[str, None] = None
    waktu_keluar: Union[datetime, date, timedelta, str, None] = None
    messages: str