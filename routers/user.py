from fastapi import APIRouter
from schemas.pemberipakan import *
from schemas.kolam import *
from schemas.notifikasi import *
from schemas.pangan import *
from db import *

#Sepertinya tidak berguna soalnya sudah ada di module auth-router.py

user_router = APIRouter(tags=["User"])

#takaranlele
@user_router.post("/inputkolamlele", summary="Mengukur Tarakan Lele")
async def takaran_leleIn(newKolam: Kolam):
    kolam = {"key": newKolam.key, 
        "JumlahLele": newKolam.JumlahLele,
        "UmurLele": newKolam.UmurLele,
        "TanggalAwalTebarBibit": newKolam.TanggalAwalTebarBibit,
        "TakaranPangan" : newKolam.TakaranPangan
    }
    hitungJumlah = newKolam.JumlahLele // newKolam.UmurLele
    kolam['TakaranPangan'] = hitungJumlah
    return db_kolam.put(kolam)

#Sepertinya langsung post di POST aja
@user_router.post("/restockin", response_model=RestockIn)
async def menghitung_restock(newRestock: RestockIn, newKolam: Kolam):
    JumlahLele = db_kolam.fetch({"key": newKolam.JumlahLele})
    restock = {
        "key": newKolam.key,
        "JumlahPakan": newRestock.JumlahPakan,
        "RestockPakan": newRestock.RestockPangan 
    }
    hitungRestockPerhari = JumlahLele
    restock['RestockPakan'] = hitungRestockPerhari
    return restock

#notifikasi
@user_router.get("/notifikasi/{id_user}")
async def notifikasi(id_user: str):
    return {"Notifikasi": id_user}

#profile admin - user
@user_router.get("/profile/{id_user}")
async def profile(id_user: str):
    return {"Profile": id_user}

#search
@user_router.get("/search/{something}")
async def search(something: str):
    return {"Search" : something}