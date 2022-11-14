from pydantic import BaseModel

class BeritaDanPedoman(BaseModel):
    key: str #AdminID
    judulBeritaDanPedoman: str
    tanggalBeritaDanPedoman: str
    isiBeritaDanPedoman: str
    fileBeritaDanPedoman: str
