from pydantic import BaseModel

class Notifikasi(BaseModel):
    key: str #Notifikasi.ID
    NotifikasiRestockPakan: str
    NotifikasiRemindHarianDanTakaran: str
    NotifikasiPengingatWaktuPanen: str