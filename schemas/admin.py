from pydantic import BaseModel

class AdminDB(BaseModel):
    key: str #AdminID
    nama_admin: str
    passwrod_admin: str