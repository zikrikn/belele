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
        "TanggalAwalTebarBibit": newKolam.TanggalAwalTebarBibit
    }
    hitungJumlah = newKolam.JumlahLele / newKolam.UmurLele
    kolam.update({"TakaranPangan": hitungJumlah})
    return kolam

#Sepertinya langsung post di POST aja

@user_router.get("/jumlahpanganout")
async def jumlahpakan_out(isiJumlahPangan: JumlahPangan):
    newTakaran = db_kolam.get(isiJumlahPangan.TakaranPangan)
    return newTakaran

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