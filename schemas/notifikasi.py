from pydantic import BaseModel

class NotifikasiDB(BaseModel):
    key: str #Notifikasi.ID
    NotifikasiRestockPakan: str
    NotifikasiRemindHarianDanTakaran: str
    NotifikasiPengingatWaktuPanen: str