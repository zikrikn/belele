from pydantic import BaseModel

class Pangan(BaseModel):
    key: str #PanganID
    JumlahStock: int


class RestockNew(Pangan):
    TakaranPangan: int
    RestockPangan: int