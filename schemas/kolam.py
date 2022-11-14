from pydantic import BaseModel

class Kolam(BaseModel):
    key: str #Kolam.id
    #PanganID: str
    #PemberiPakanID: str
    NamaKolam: str
    JumlahLele: str
    UmurLele: int
    TanggalAwalTebarBibit: str