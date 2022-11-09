from pydantic import BaseModel

class PemberiPakan(BaseModel):
    key: str #PemberiPakanID
    NamaPemberiPakan: str
    PasswordPP: str