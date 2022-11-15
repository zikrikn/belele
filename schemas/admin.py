from pydantic import BaseModel

class AdminDB(BaseModel):
    key: str #AdminID
    NamaAdmin: str
    PasswrodAdmin: str