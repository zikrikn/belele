from fastapi import APIRouter
from schemas.beritadanpedoman import *
from schemas.pemberipakan import *
from schemas.admin import *
from db import *

both_router = APIRouter(tags=["Both"])

#Berita
@both_router.get("/berita")
async def berita(berita: BeritaDanPedomanDB):
    req_berita = db_beritadanpedoman.fetch({"tipe": "berita"})
    return req_berita.items

#Pedoman
@both_router.get("/pedoman")
async def pedoman(pedoman: BeritaDanPedomanDB):
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    return req_pedoman.items

#profile admin - user
@user_router.get("/profile/{id_user}")
async def profile(id_user: str):
    user = db_pemberipakan.fetch({'key': user_id})
    admin = db_admin.fetch({'key', user_id})

    if len(user.items) != 0:
        return user.items[0]

    if len(admin.items) != 0:
        return admin.items[0]
    

#Logout
@both_router.post("/logout")
async def logout():
    return "Logout"