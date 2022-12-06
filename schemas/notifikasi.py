from pydantic import BaseModel
from typing import Union
from datetime import datetime, date, timedelta

class inputNotifikasi(BaseModel):
    key: str #Notifikasi.ID
    tipe: str
    waktuMasuk: Union[datetime, date, timedelta, str, None] = None
    waktuKeluar: Union[datetime, date, timedelta, str, None] = None
    waktuHabis: Union[datetime, date, timedelta, str, None] = None

class outputNotifikasi(BaseModel):
    key: str #Notifikasi.ID
    tipe: str
    waktuKeluar: Union[datetime, date, timedelta, str, None] = None
    messages: str