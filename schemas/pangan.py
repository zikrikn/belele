from pydantic import BaseModel

class PanganDB(BaseModel):
    key: str #PanganID
    JumlahStock: int


class RestockNew(PanganDB):
    TakaranPangan: int
    RestockPangan: int