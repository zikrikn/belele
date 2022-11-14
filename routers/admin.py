from fastapi import APIRouter

admin_router = APIRouter()

#admin - berita
@admin_router.post("/post/berita", tags=["admin"])
async def postBerita():
    return "Post Berita"

#admin - pedoman
@admin_router.post("/post/pedoman", tags=("admin"))
async def postPedoman():
    return "Pist Pedoman"

#admin - delete berita
@admin_router.delete("/delete/berita", tags=("admin"))
async def deleteBerita():
    return "Delete Berita"

#admin - delete pedoman
@admin_router.delete("/delete/pedoman", tags=("admin"))
async def deletePedoman():
    return "Delete Pedoman"