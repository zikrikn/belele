from pydantic import BaseModel
from typing import Union
from datetime import datetime, date, timedelta
from schemas.const import Base

class KolamDB(Base):
    key: str
    nama_kolam: str #Kolam.idr
    jumlah_lele: int
    berat_lele: int
    stock_pakan: Union[float, None] = None
    waktu_tebar: Union[datetime, date, timedelta, str, None] = None
    jumlah_pakan_harian: Union[float, None] = None
    waktu_panen: Union[datetime, date, timedelta, str, None] = None
    waktu_restock: Union[datetime, date, timedelta, str, None] = None
    allow_restock_ulang: bool

class KolamIn(BaseModel):
    nama_kolam: str #Kolam.idr
    jumlah_lele: int
    berat_lele: int
    stock_pakan: Union[float, None] = None

class RestockOut(BaseModel): #This Out
    nama_kolam: str #Kolam.id
    waktu_restock: Union[datetime, date, timedelta, str, None] = None

class RestockUlangOut(BaseModel): #This Out
    nama_kolam: str #Kolam.id
    jumlah_pakan_harian: Union[float, None] = None
    stock_pakan: Union[float, None] = None
    waktu_restock: Union[datetime, date, timedelta, str, None] = None