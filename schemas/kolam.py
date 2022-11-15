from pydantic import BaseModel

class Kolam(BaseModel):
    key: str #Kolam.idr
    JumlahLele: int
    UmurLele: int
    TanggalAwalTebarBibit: str
    TakaranPangan: int

class RestockIn(BaseModel): #This in
    key: str #Kolam.id
    JumlahPakan: int
    RestockPangan: int

class RestockOut(BaseModel): #This in
    key: str #Kolam.id
    JumlahPakan: int
    RestockPangan: int
