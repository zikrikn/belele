from fastapi import APIRouter, HTTPException, Path, Query
from schemas.pemberipakan import *
from schemas.kolam import *
from schemas.notifikasi import *
from schemas.pangan import *
from db import *
from pydantic import ValidationError

#Sepertinya tidak berguna soalnya sudah ada di module auth-router.py

user_router = APIRouter(tags=["User"])

#takaranlele
@user_router.post("/inputkolamlele", summary="Mengukur Tarakan Lele", response_model=KolamIn)
async def takaran_leleIn(newKolam: KolamDB):
    req_kolam = db_kolam.fetch({'key': newKolam.key})
    if len(req_kolam.items) != 0:
        raise HTTPException(
            status_code=400,
            detail="Data already exist"
        )

    kolam = {"key": newKolam.key, 
        "JumlahLele": newKolam.JumlahLele,
        "BeratLele": newKolam.BeratLele,
        "TanggalAwalTebarBibit": newKolam.TanggalAwalTebarBibit,
        "TakaranPangan": newKolam.TakaranPangan,
        "JumlahPakan": newKolam.JumlahPakan,
        "RestockPakan": newKolam.RestockPangan
    }
    hitungJumlah = newKolam.JumlahLele // newKolam.BeratLele
    kolam['TakaranPangan'] = hitungJumlah

    try:
        validated_new_profile = KolamDB(**kolam)
        db_kolam.put(kolam)
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )
    return kolam

#Sepertinya langsung post di POST aja
@user_router.post("/restock", summary="Merestock pakan lele", response_model=RestockOut)
async def menghitung_restock(newRestock: RestockIn):
    req_restock = db_kolam.fetch({"key": newRestock.key})
    if len(req_restock.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )

    update = {
        "JumlahPakan": newRestock.JumlahPakan,
        "RestockPakan": hasilrestockpakan
    }

    assign_restock = req_restock.items[0]
    hasilrestockpakan = newRestock.JumlahPakan * assign_restock['BeratLele'] * (3/100)

    assign_restock['JumlahPakan'] = newRestock.JumlahPakan
    assign_restock['RestockPakan'] = hasilrestockpakan\
    
    try:
        validated_new_profile = KolamDB(**kolam)
        db_kolam.update(update, assign_restock['key'])
        #db_kolam.put(kolam)
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )
    #db_kolam.update(update, assign_restock['key'])

    return assign_restock

#notifikasi //buat trigger atau gak refresh setiap berapa menit sekali //atau tentukan waktu untuk trigger
@user_router.get("/notifikasi/{id_user}")
async def notifikasi(id_user: str):
    return {"Notifikasi": id_user}

#search
@user_router.get("/search/{something}")
async def search(something: str):
    req_search = db_kolam.fetch({'key': something}) #use fixed query
    if len(req_search.items) == 0:
            raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )

    return req_search.items