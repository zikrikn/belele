from fastapi import APIRouter, HTTPException
from schemas.pemberipakan import *
from schemas.kolam import *
from schemas.notifikasi import *
from schemas.pangan import *
from db import *
from pydantic import ValidationError

#Sepertinya tidak berguna soalnya sudah ada di module auth-router.py

user_router = APIRouter(tags=["User"])

#takaranlele
@user_router.post("/inputkolamlele", summary="Mengukur Tarakan Lele")
async def takaran_leleIn(newKolam: KolamDB):
    req_kolam = db_kolam.fetch({'key': newKolam.key})
    if len(req_kolam.items) != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data already exist"
        )

    kolam = {"key": newKolam.key, 
        "JumlahLele": newKolam.JumlahLele,
        "UmurLele": newKolam.UmurLele,
        "TanggalAwalTebarBibit": newKolam.TanggalAwalTebarBibit,
        "TakaranPangan" : newKolam.TakaranPangan
    }
    hitungJumlah = newKolam.JumlahLele // newKolam.UmurLele
    kolam['TakaranPangan'] = hitungJumlah

    try:
        validated_new_profile = KolamDB(**kolam)
        db_kolam.put(kolam)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input value"
        )
    return kolam

#Sepertinya langsung post di POST aja
@user_router.post("/restock", summer)
async def menghitung_restock():
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