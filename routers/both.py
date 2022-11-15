from fastapi import APIRouter
from schemas.beritadanpedoman import *
from schemas.pemberipakan import *
from schemas.admin import *
from db import *

both_router = APIRouter(tags=["Both"])

#Berita
@both_router.get("/berita")
async def berita():
    return "Berita"

#Pedoman
@both_router.get("/pedoman")
async def pedoman():
    return "Pedoman"

#Logout
@both_router.post("/logout")
async def logout():
    return "Logout"