from fastapi import APIRouter

#Sepertinya tidak berguna soalnya sudah ada di module auth-router.py

user_router = APIRouter()

#remindrestock
@user_router.post("/restockpakan/", tags=["users"])
def remindrestock():
    return "Restock"

#takaranlele
@user_router.post("/inputkolamlele/", tags=("users"))
def takaranlele():
    return "Takaran Lele"

#notifikasi
@user_router.get("/notifikasi/{id_user}", tags=("users"))
def notifikasi(id_user: str):
    return "Notifikasi {id_user}"

#profile admin - user
@user_router.get("/profile/{id_user}", tags=("users"))
def profile(id_user: str):
    return "Profile {id_user}"

#search
@user_router.get("/search/{something}", tags=("users"))
def search(something: str):
    return "Search {something}"