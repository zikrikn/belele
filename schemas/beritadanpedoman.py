from pydantic import BaseModel
from typing import Union

class BeritaDanPedomanDB(BaseModel):
    key: str 
    tipe: str
    judul_berita_dan_pedoman: str
    tanggal_berita_dan_pedoman: str
    isi_berita_dan_pedoman: str
    thumbnail: Union[str, None] = None

class BeritaDanPedomanIn(BaseModel):
    judul_berita_dan_pedoman: str
    #tanggal_berita_dan_pedoman: str
    isi_berita_dan_pedoman: str
    #thumbnail: str