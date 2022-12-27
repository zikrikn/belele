from pydantic import BaseModel

class PemberiPakanDB(BaseModel):
    key: str #PemberiPakanID
    nama_pemberipakan: str
    password_pemberipakan: str

class PemberiPakanIn(BaseModel):
    key: str #PemberiPakanID
    password_pemberipakan: str