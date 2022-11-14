from fastapi import APIRouter

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