from pydantic import BaseModel

class Admin(BaseModel):
    key: str #AdminID
    NamaAdmin: str
    PasswrodAdmin: str