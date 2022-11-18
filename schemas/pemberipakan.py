from pydantic import BaseModel

class PemberiPakanDB(BaseModel):
    key: str #PemberiPakanID
    NamaPemberiPakan: str
    PasswordPP: str

class PemberiPakanIn(BaseModel):
    key: str #PemberiPakanID
    PasswordPP: str