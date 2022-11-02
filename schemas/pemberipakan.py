from pydantic import BaseModel

class PemberiPakan(BaseModel):
    PemberiPakanID: str
    NamaPemberiPakan: str
    PasswordPP: str