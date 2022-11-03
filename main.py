from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat
from schemas.admin import Admin
from schemas.kolam import *
from db_and_drive import *

#Fokus untuk membuat REST API-nya buat backend

app = FastAPI()

@app.get("/hi")
async def main():
    return {"message": "Hello World"}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/users", status_code=201)
def create_user(user: Admin):
    pengguna = db_admin.put(user.dict())
    return pengguna

app.add_middleware(
    CORSMiddleware,
    #allow_origins=['http://app.lemes.my.id', 'https://app.lemes.my.id'],
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)