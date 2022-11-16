from pydantic import BaseModel
from typing import Union

class KolamDB(BaseModel):
    NamaKolam: str #Kolam.idr
    JumlahLele: int
    BeratLele: int
    TanggalAwalTebarBibit: str
    TakaranPangan: int
    JumlahPakan: Union[int, None] = None
    RestockPangan: Union[int, None] = None

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
    JumlahPakan: int
    RestockPangan: int