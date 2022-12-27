from pydantic import BaseModel

class BeritaDanPedomanDB(BaseModel):
    key: str #ID dari agar terupdate dari yang paling baru
    tipe: str #Tipe-nya Berita atau Pedoman
    judul_berita_dan_pedoman: str
    tanggal_berita_dan_pedoman: str
    isi_berita_dan_pedoman: str
    file_berita_dan_pedoman: str

class BeritaDanPedomanIn(BaseModel):
    judul_berita_dan_pedoman: str
    tanggal_berita_dan_pedoman: str
    isi_berita_dan_pedoman: str
    file_berita_dan_pedoman: str