from pydantic import BaseModel

class PanganDB(BaseModel):
    key: str #PanganID
    JumlahStock: int


class RestockNew(Pangan):
    TakaranPangan: int
    RestockPangan: int