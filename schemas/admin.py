from pydantic import BaseModel

class Admin(BaseModel):
    AdminID: str
    NamaAdmin: str
    PasswrodAdmin: str