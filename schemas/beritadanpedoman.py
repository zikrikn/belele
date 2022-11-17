from pydantic import BaseModel

class BeritaDanPedomanDB(BaseModel):
    key: str #ID dari agar terupdate dari yang paling baru
    tipe: str #Tipe-nya Berita atau Pedoman
    judulBeritaDanPedoman: str
    tanggalBeritaDanPedoman: str
    isiBeritaDanPedoman: str
    fileBeritaDanPedoman: str

class BeritaDanPedomanIn(BaseModel):
    judulBeritaDanPedoman: str
    tanggalBeritaDanPedoman: str
    isiBeritaDanPedoman: str
    fileBeritaDanPedoman: str