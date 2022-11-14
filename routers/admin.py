from fastapi import APIRouter

admin_router = APIRouter()

#admin - berita
@admin_router.post("/post/berita", tags=["admin"])
def postBerita():
    return "Post Berita"

#admin - pedoman
@admin_router.post("/post/pedoman", tags=("admin"))
def postPedoman():
    return "Pist Pedoman"

#admin - delete berita
@admin_router.delete("/delete/berita", tags=("admin"))
def deleteBerita():
    return "Delete Berita"

#admin - delete pedoman
@admin_router.delete("/delete/pedoman", tags=("admin"))
def deletePedoman():
    return "Delete Pedoman"