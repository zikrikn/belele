from fastapi import APIRouter
from schemas.pemberipakan import *
from schemas.kolam import *
from schames.notifikasi import *
from schames.pangan import *
from db import *

#Sepertinya tidak berguna soalnya sudah ada di module auth-router.py

user_router = APIRouter(tags=["User"])

#takaranlele
@user_router.post("/inputkolamlele", summary="Mengukur Tarakan Lele", response_model=Kolam)
async def takaran_leleIn(newKolam: Kolam):
    newKolam1 = db_kolam.put(newKolam.dict())
    return newKolam1

#jumlahpakan
#! IN
@user_router.post("/jumlahpanganin", summary="Menghitung Jumlah Pakan", response_model=JumlahPangan)
async def Jumlah_Pangan(kolam_details: Kolam):
    if db.kolam.get(kolam_details.key) != None:
        jumlahLele = db_kolam.fetch({"JumlahLele": kolam_details.JumlahLele})
        umurLele = db_kolam.fetch({"UmurLele": kolam_details.UmurLele})
        UkuranTakar = jumlahLele / umurLele
        hasilUkur = db_kolam.put({"key": kolam_details.key, "TakaranPangan": UkuranTakar})
        return hasilUkur
    else:
        return "Data Invalid"

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