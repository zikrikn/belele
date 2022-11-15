from pydantic import BaseModel

class BeritaDanPedomanDB(BaseModel):
    key: str #AdminID
    judulBeritaDanPedoman: str
    tanggalBeritaDanPedoman: str
    isiBeritaDanPedoman: str
    fileBeritaDanPedoman: str
