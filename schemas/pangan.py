from pydantic import BaseModel

class Pangan(BaseModel):
    key: str #PanganID
    JumlahStock: int
    TakaranPangan: int
    RestockPangan: int