from fastapi import FastAPI, File, UploadFile 
# File dan UploadFile untuk Drive
# For Drive
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya
from schemas.admin import Admin
from schemas.kolam import *
from db import *

# Fokus untuk membuat REST API-nya buat backend

app = FastAPI(
    title="LeMES",
    version="1.0",
    prefix="/api"
)

# For Drive Images
drive = deta.Drive("images")

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

@app.get("/imgs", response_class=HTMLResponse)
def render():
    return """
    <form action="/upload" enctype="multipart/form-data" method="post">
        <input name="file" type="file">
        <input type="submit">
    </form>
    """

@app.post("/upload")
def upload_img(file: UploadFile = File(...)):
    name = file.filename
    f = file.file
    res = drive.put(name, f)
    return res

@app.get("/download/{name}")
def download_img(name: str):
    res = drive.get(name)
    return StreamingResponse(res.iter_chunks(1024), media_type="image/png")

app.add_middleware(
    CORSMiddleware,
    #allow_origins=['http://app.lemes.my.id', 'https://app.lemes.my.id'],
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

