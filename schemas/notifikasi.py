from pydantic import BaseModel
from typing import Union

class NotifikasiDB(BaseModel):
    key: str #Notifikasi.ID
    NotifikasiRestockPakan: Union[bool, None] = None
    NotifikasiRemindHarianTakaranWaktuPanen : Union[bool, None] = None