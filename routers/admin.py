from fastapi import APIRouter
from schemas.beritadanpedoman import *
from db import *

admin_router = APIRouter(tags=["Admin"])

#admin - berita
@admin_router.post("/post/berita")
async def post_berita():
    return "Post Berita"

#admin - pedoman
@admin_router.post("/post/pedoman")
async def post_Pedoman():
    return "Pist Pedoman"

#admin - delete berita
@admin_router.delete("/delete/berita")
async def delete_berita():
    return "Delete Berita"

#admin - delete pedoman
@admin_router.delete("/delete/pedoman")
async def delete_pedoman():
    return "Delete Pedoman"