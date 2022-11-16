from fastapi import APIRouter
from schemas.beritadanpedoman import *
from db import *

admin_router = APIRouter(tags=["Admin"])

#admin - berita
@admin_router.post("/post/berita")
async def post_berita(berita: BeritaDanPedomanDB):
    berita = {
        "key": berita.key,
        "tipe": berita.tipe,
        "judulBeritaDanPedoman": berita.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": berita.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": berita.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": berita.fileBeritaDanPedoman
    }
    return berita

#admin - pedoman
@admin_router.post("/post/pedoman")
async def post_Pedoman(pedoman: BeritaDanPedomanDB):
    pedoman = {
        "key": pedoman.key,
        "tipe": pedoman.tipe,
        "judulBeritaDanPedoman": pedoman.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": pedoman.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": pedoman.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": pedoman.fileBeritaDanPedoman
    }
    return pedoman

#admin - delete berita
@admin_router.delete("/delete/beritadanpedoman")
async def delete_berita(berita: BeritaDanPedomanDB):
    req_berita = db_beritadanpedoman.fetch({"tipe": berita.judulBeritaDanPedoman})
    db_beritadanpedoman.delete(req_berita.items['0']['key'])
    return {'message': 'success'}