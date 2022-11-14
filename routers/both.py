from fastapi import APIRouter

both_router = APIRouter()

#Berita
@both_router.get("/berita", tags=["both"])
async def berita():
    return "Berita"

#Pedoman
@both_router.get("/pedoman", tags=("both"))
async def pedoman():
    return "Pedoman"

#Logout
@both_router.post("/logout", tags=("both"))
async def logout():
    return "Logout"