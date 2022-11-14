from fastapi import APIRouter

both_router = APIRouter()

#Berita
@both_router.get("/berita", tags=["both"])
def berita():
    return "Berita"

#Pedoman
@both_router.get("/pedoman", tags=("both"))
def pedoman():
    return "Pedoman"

#Logout
@both_router.post("/logout", tags=("both"))
def logout():
    return "Logout"