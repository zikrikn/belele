from pydantic import BaseModel

class BeritaDanPedomanDB(BaseModel):
    tipe: str #Tipe-nya Berita atau Pedoman
    judulBeritaDanPedoman: str
    tanggalBeritaDanPedoman: str
    isiBeritaDanPedoman: str
    fileBeritaDanPedoman: str
