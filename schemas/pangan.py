from pydantic import BaseModel

class Pangan(BaseModel):
    PanganID: str
    JumlahStock: int
    TakaranPangan: int
    RestockPangan: int