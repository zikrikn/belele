from pydantic import BaseModel

class PemberiPakanDB(BaseModel):
    key: str #PemberiPakanID
    NamaPemberiPakan: str
    PasswordPP: str