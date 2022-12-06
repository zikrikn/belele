from pydantic import BaseModel
from typing import Union

class KolamDB(BaseModel):
    key: str
    NamaKolam: str #Kolam.idr
    JumlahLele: int
    BeratLele: int
    TanggalAwalTebarBibit: str
    TakaranPangan: Union[float, None] = None
    JumlahPakan: Union[float, None] = None
    RestockPangan: Union[float, None] = None

class KolamIn(BaseModel):
    NamaKolam: str #Kolam.idr
    JumlahLele: int
    BeratLele: int
    TanggalAwalTebarBibit: str

class RestockIn(BaseModel): #This Out
    NamaKolam: str #Kolam.id
    #BeratLele: int
    JumlahPakan: int

class RestockOut(BaseModel): #This Out
    NamaKolam: str #Kolam.id
    BeratLele: int
    JumlahPakan: Union[float, None] = None
    RestockPangan: Union[float, None] = None