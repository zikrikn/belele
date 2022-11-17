from fastapi import FastAPI, HTTPException, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya OR using NEXT.js
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
import time

#Schemas
from schemas.pemberipakan import *
from schemas.kolam import *
from schemas.notifikasi import *
from schemas.pangan import *
from schemas.admin import *
from schemas.beritadanpedoman import *

#Connecting to database
from db import *

#Unicorn
import uvicorn

'''
#Routers
from routers.admin import admin_router
from routers.both import both_router
from routers.user import user_router
'''

#Auth
from auth_subpackage.auth_router import *

#Database
from db import *

app = FastAPI(
    title="LeMES",
    version="1.0",
    prefix="/api"
)

@app.get("/", include_in_schema=False)
async def redirect_docs():
    print("Hello Wolrd")
    return RedirectResponse("/docs")

''''''''''''
#!! USER !!
''''''''''''

user_router = APIRouter(tags=["User"])

#takaranlele
@user_router.post("/inputkolamlele", summary="Mengukur Tarakan Lele", response_model=KolamIn)
async def takaran_leleIn(newKolam: KolamDB):
    req_kolam = db_kolam.fetch({'NamaKolam': newKolam.NamaKolam})
    if len(req_kolam.items) != 0:
        raise HTTPException(
            status_code=400,
            detail="Data already exist"
        )

    kolam = {"NamaKolam": newKolam.NamaKolam, 
        "JumlahLele": newKolam.JumlahLele,
        "BeratLele": newKolam.BeratLele,
        "TanggalAwalTebarBibit": newKolam.TanggalAwalTebarBibit,
        "TakaranPangan": newKolam.TakaranPangan,
        "JumlahPakan": newKolam.JumlahPakan,
        "RestockPakan": newKolam.RestockPangan
    }

    hasiljumlah = newKolam.BeratLele * (3/100)
    print(hasiljumlah)
    kolam['TakaranPangan'] = hasiljumlah

    try:
        validated_new_profile = KolamDB(**kolam)
        db_kolam.put(validated_new_profile.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )
    return kolam

@user_router.post("/restock", summary="Merestock pakan lele", response_model=RestockOut)
def menghitung_restock(newRestock: RestockIn):
    req_restock = db_kolam.fetch({'NamaKolam': newRestock.NamaKolam})
    if len(req_restock.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )

    assign_restock = req_restock.items[0]
    totalrestock = newRestock.JumlahPakan / assign_restock['BeratLele'] * (3/100)
    print(totalrestock)
    
    update = {
        "JumlahPakan": newRestock.JumlahPakan,
        "RestockPangan": totalrestock
    }

    assign_restock['JumlahPakan'] = newRestock.JumlahPakan
    assign_restock['RestockPangan'] = totalrestock
    
    db_kolam.update(update, assign_restock['key'])

    return assign_restock

#search
@user_router.get("/search/{something}")
async def search(something: str):
    req_search = db_kolam.fetch({'NamaKolam': something}) #use fixed query
    if len(req_search.items) == 0:
            raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )

    return req_search.items

#notifikasi //buat trigger atau gak refresh setiap berapa menit sekali //atau tentukan waktu untuk trigger //menggunakan deta webhook sebagai alternative
@user_router.get("/notifikasi/{id_user}")
async def notifikasi(id_user: str):
    return {"Notifikasi": id_user}

''''''''''''
#!! BOTH !!
''''''''''''

both_router = APIRouter(tags=["Both"])

#Berita
@both_router.get("/berita")
async def berita():
    req_berita = db_beritadanpedoman.fetch({"tipe": "berita"})
    if len(req_berita.items) == 0:
        raise HTTPException(
        status_code=400,
        detail="Laman Berita Kosong"
        )
    
    isiberita = req_berita.items
    # PR buat sorting untuk menampilkan isi JSON yang paling recent
    return isiberita

#Pedoman
@both_router.get("/pedoman")
async def pedoman():
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    if len(req_pedoman.items) == 0:
        raise HTTPException(
        status_code=400,
        detail="Laman Berita Kosong"
        )
    
    isipedoman = req_pedoman.items
    return isipedoman

#profile admin - user
@both_router.get("/profile/{id_user}")
async def profile(id_user: str):
    user = db_pemberipakan.fetch({'key': id_user})
    admin = db_admin.fetch({'key', id_user})

    if len(user.items) != 0:
        return user.items[0]

    if len(admin.items) != 0:
        return admin.items[0]
    

#Logout
@both_router.post("/logout")
async def logout():
    return "Logout"

''''''''''''
#!! ADMIN !!
''''''''''''
admin_router = APIRouter(tags=["Admin"])

#fungsi untuk generate key agar lastest record muncul paling atas

def generateKey(timestap):
    bigNumber = 8.64e15
    return (bigNumber - timestap)

#admin - berita
@admin_router.post("/post/berita", response_model=BeritaDanPedomanDB)
async def post_berita(berita: BeritaDanPedomanIn):

    berita = {
        "key": str(int(generateKey(time.time() * 10000))),
        "tipe": "berita",
        "judulBeritaDanPedoman": berita.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": berita.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": berita.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": berita.fileBeritaDanPedoman
    }
    return db_beritadanpedoman.put(berita)

#admin - pedoman
@admin_router.post("/post/pedoman", response_model=BeritaDanPedomanDB)
async def post_Pedoman(pedoman: BeritaDanPedomanIn):

    pedoman = {
        "key": str(int(generateKey(time.time() * 10000))),
        "tipe": "pedoman",
        "judulBeritaDanPedoman": pedoman.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": pedoman.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": pedoman.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": pedoman.fileBeritaDanPedoman
    }
    return db_beritadanpedoman.put(pedoman)

#admin - delete berita
@admin_router.delete("/delete/berita")
async def delete_berita():
    req_berita = db_beritadanpedoman.fetch({"tipe": "berita"})
    print(req_berita)
    db_beritadanpedoman.delete(req_berita.items[0]['key'])
    return {'message': 'success'}

#admin - delete pedoman
@admin_router.delete("/delete/pedoman")
async def delete_pedoman():
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    db_beritadanpedoman.delete(req_pedoman.items[0]['key'])
    return {'message': 'success'}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(both_router)

app.add_middleware(
    CORSMiddleware,
    #allow_origins=['http://app.lemes.my.id', 'https://app.lemes.my.id'],
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

