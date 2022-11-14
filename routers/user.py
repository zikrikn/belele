from fastapi import APIRouter
from schemas.pemberipakan import *
from schemas.kolam import *
from schames.notifikasi import *
from schames.pangan import *
from db import *

#Sepertinya tidak berguna soalnya sudah ada di module auth-router.py

user_router = APIRouter(tags=["User"])

#remindrestock
@user_router.post("/restockpakan/")
async def remind_restock():
    return "Restock"

#takaranlele
@user_router.post("/inputkolamlele/")
async def takaran_lele():
    return "Takaran Lele"

#notifikasi
@user_router.get("/notifikasi/{id_user}")
async def notifikasi(id_user: str):
    return {"Notifikasi": id_user}

#profile admin - user
@user_router.get("/profile/{id_user}")
async def profile(id_user: str):
    return "Profile {id_user}"

#search
@user_router.get("/search/{something}")
async def search(something: str):
    return "Search {something}"