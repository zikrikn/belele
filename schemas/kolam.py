from pydantic import BaseModel

class Kolam(BaseModel):
    key: str #Kolam.id
    #PanganID: str
    #PemberiPakanID: str
    JumlahLele: str
    UmurLele: int
    TanggalAwalTebarBibit: str
    TakaranPangan: int

#Ini nanti yang hanya dikeluarkan pake response model
class JumlahPangan(BaseModel): #This out
    key: str #Kolam.id
    TakaranPangan: int #Ini berarti auto generate ukuran pakan secara menyeluruh sesuai dengan input user di class Kolam

class RestockIn(BaseModel): #This in
    key: str #Kolam.id
    JumlahPakan: int
    RestockPangan: int

