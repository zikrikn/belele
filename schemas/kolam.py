from pydantic import BaseModel

class Kolam(BaseModel):
    KolamID: str
    PanganID: str
    JumlahLele: str
    TanggalAwalTebarBibit: str
    UmurLele: int
    BeratLele: int