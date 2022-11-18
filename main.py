from fastapi import FastAPI, HTTPException, APIRouter, Security
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya OR using NEXT.js
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
import time

# Schemas
from schemas.pemberipakan import *
from schemas.kolam import *
from schemas.notifikasi import *
from schemas.pangan import *
from schemas.admin import *
from schemas.beritadanpedoman import *

# Connecting to database
from db import *

# Unicorn
import uvicorn

# Auth
from auth_class import *
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

#Auto handler
security = HTTPBearer()
auth_handler = Auth()

'''
#Routers
from routers.admin import admin_router
from routers.both import both_router
from routers.user import user_router
'''

app = FastAPI(
    title="LeMES",
    version="1.0",
    prefix="/api"
)

#fungsi untuk generate key agar lastest record muncul paling atas
def generateKey(timestap):
    bigNumber = 8.64e15
    return (bigNumber - timestap)

@app.get("/", include_in_schema=False)
async def redirect_docs():
    return RedirectResponse("/docs")

''''''''''''
#!! AUTH !!
''''''''''''
auth_router = APIRouter(tags=["Auth"])

#Membuat auth untuk login dan signup
#!!!Tambahannya signup admin dan delete akun!!!

@auth_router.post('/signup')
async def signup(user_details: PemberiPakanDB):
    if db_pemberipakan.get(user_details.key) != None:
        return 'Account already exists'
    try:
        hashed_password = auth_handler.encode_password(user_details.PasswordPP)
        user = {'key': user_details.key, 'password': hashed_password}
        return db_pemberipakan.put(user)
    except:
        error_msg = 'Failed to signup user'
        return error_msg

@auth_router.post('/login')
async def login(user_details: PemberiPakanIn):
    user = db_pemberipakan.get(user_details.key)
    if (user is None):
        return HTTPException(status_code=401, detail='Invalid username')
    if (not auth_handler.verify_password(user_details.PasswordPP, user['password'])):
        return HTTPException(status_code=401, detail='Invalid password')
    
    access_token = auth_handler.encode_token(user['key'])
    refresh_token = auth_handler.encode_refresh_token(user['key'])
    return {'access_token': access_token, 'refresh_token': refresh_token}

@auth_router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token}


@auth_router.post('/secret')
def secret_data(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return 'Top Secret data only authorized users can access this info'

@auth_router.get('/notsecret')
def not_secret_data():
    return 'Not secret data'

''''''''''''
#!! USER !!
''''''''''''

user_router = APIRouter(tags=["User"])

#takaranlele
@user_router.post("/inputkolamlele", summary="Mengukur Tarakan Lele", response_model=KolamIn)
async def takaran_leleIn(newKolam: KolamIn, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        req_kolam = db_kolam.fetch({'NamaKolam': (newKolam.NamaKolam).lower()})
        if len(req_kolam.items) != 0:
            raise HTTPException(
                status_code=400,
                detail="Data already exist"
            )

        kolam = {
            "key": str(int(generateKey(time.time() * 10000))),
            "NamaKolam": (newKolam.NamaKolam).lower(), 
            "JumlahLele": newKolam.JumlahLele,
            "BeratLele": newKolam.BeratLele,
            "TanggalAwalTebarBibit": newKolam.TanggalAwalTebarBibit,
            "TakaranPangan": newKolam.TakaranPangan,
            "JumlahPakan": 0,
            "RestockPakan": 0
        }

        hasiljumlah = newKolam.BeratLele * (3/100)
        print(hasiljumlah)
        kolam['TakaranPangan'] = hasiljumlah

        Notifikasi = {
            "key": str(int(generateKey(time.time() * 10000))),
            "NotifikasiRemindHarianTakaranWaktuPanen": True
        }

        db_notifikasi.put(Notifikasi)

        try:
            validated_new_profile = KolamDB(**kolam)
            db_kolam.put(validated_new_profile.dict())
        except ValidationError:
            raise HTTPException(
                status_code=404,
                detail="Invalid input value"
            )
        return kolam

@user_router.post("/restock", summary="Merestock pakan lele", response_model=RestockOut)
def menghitung_restock(newRestock: RestockIn, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        req_restock = db_kolam.fetch({'NamaKolam': (newRestock.NamaKolam).lower()})
        if len(req_restock.items) == 0:
            raise HTTPException(
                status_code=400,
                detail="Data not exist"
            )

        assign_restock = req_restock.items[0]
        totalrestock = newRestock.JumlahPakan / assign_restock['BeratLele'] * (3/100)
        print(totalrestock)
        
        update = {
            "JumlahPakan": newRestock.JumlahPakan,
            "RestockPangan": totalrestock
        }

        assign_restock['JumlahPakan'] = newRestock.JumlahPakan
        assign_restock['RestockPangan'] = totalrestock
        
        db_kolam.update(update, assign_restock['key'])

        Notifikasi = {
            "key": str(int(generateKey(time.time() * 10000))),
            "NotifikasiRestockPakan": True
        }

        db_notifikasi.put(Notifikasi)

        return assign_restock

#get info kolam
@user_router.get("/infokolam", summary="Melihat Info Kolam")
async def info_kolam(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        res_kolam = db_kolam.fetch()
        all_items = res_kolam.items

        if len(all_items) == 0:
                raise HTTPException(
                status_code=400,
                detail="Tidak ada data kolam"
            )
        
        return all_items

#delete kolam
@user_router.delete("/delete/{keykolam}", summary="Menghapus Kolam")
async def delete_kolam(keykolam: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        req_kolam = db_kolam.get(keykolam)
        namakolam = req_kolam['NamaKolam']
        db_kolam.delete(req_kolam['key'])

        return {'message': 'success', 'namakolam': namakolam}

#search
@user_router.get("/search/{something}")
async def search(something: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        req_search = db_kolam.fetch({'NamaKolam': (something).lower()}) #use fixed query
        if len(req_search.items) == 0:
                raise HTTPException(
                status_code=400,
                detail="Data not exist"
            )

        return req_search.items

#notifikasi //buat trigger atau gak refresh setiap berapa menit sekali //atau tentukan waktu untuk trigger //menggunakan deta webhook sebagai alternative
@user_router.get("/notifikasi/{id_user}")
async def notifikasi(id_user: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return {"Notifikasi": id_user}

''''''''''''
#!! ADMIN !!
''''''''''''
admin_router = APIRouter(tags=["Admin"])

#admin - berita
@admin_router.post("/post/berita", response_model=BeritaDanPedomanDB)
async def post_berita(berita: BeritaDanPedomanIn):

    berita = {
        "key": str(int(generateKey(time.time() * 10000))),
        "tipe": "berita",
        "judulBeritaDanPedoman": berita.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": berita.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": berita.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": berita.fileBeritaDanPedoman
    }
    return db_beritadanpedoman.put(berita)

#admin - pedoman
@admin_router.post("/post/pedoman", response_model=BeritaDanPedomanDB)
async def post_Pedoman(pedoman: BeritaDanPedomanIn):

    pedoman = {
        "key": str(int(generateKey(time.time() * 10000))),
        "tipe": "pedoman",
        "judulBeritaDanPedoman": pedoman.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": pedoman.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": pedoman.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": pedoman.fileBeritaDanPedoman
    }
    return db_beritadanpedoman.put(pedoman)

#admin - delete berita //nanti pakai key-nya untuk menghapus
@admin_router.delete("/delete/berita")
async def delete_berita():
    req_berita = db_beritadanpedoman.fetch({"tipe": "berita"})
    db_beritadanpedoman.delete(req_berita.items[0]['key'])
    return {'message': 'success'}

# admin - delete pedoman - the lastest 
# maybe we can changes this into by "key"
@admin_router.delete("/delete/pedoman")
async def delete_pedoman():
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    db_beritadanpedoman.delete(req_pedoman.items[0]['key'])
    return {'message': 'success'}

# untuk menghapus pedoman dengan klik lewat trigger kunci-nya yang bakal dilihat kunci-nya dari artikel yang sedang dilihat
@admin_router.delete("/delete/pedoman-byclick")
async def delete_pedomanklik(kunci: BeritaDanPedomanDB):
    req_pedoman = db_beritadanpedoman.fetch({"key": kunci})
    db_beritadanpedoman.delete(req_pedoman.items[0]['key'])
    return {'message': 'success'}

''''''''''''
#!! BOTH !!
''''''''''''

both_router = APIRouter(tags=["Both"])

#Berita
@both_router.get("/berita")
async def berita():
    req_berita = db_beritadanpedoman.fetch({"tipe": "berita"})
    if len(req_berita.items) == 0:
        raise HTTPException(
        status_code=400,
        detail="Laman Berita Kosong"
        )
    
    isiberita = req_berita.items
    # PR buat sorting untuk menampilkan isi JSON yang paling recent
    return isiberita

#Pedoman
@both_router.get("/pedoman")
async def pedoman():
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    if len(req_pedoman.items) == 0:
        raise HTTPException(
        status_code=400,
        detail="Laman Berita Kosong"
        )
    
    isipedoman = req_pedoman.items
    return isipedoman

#profile admin - user
@both_router.get("/profile/{id_user}")
async def profile(id_user: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        user = db_pemberipakan.fetch({'key': id_user})
        admin = db_admin.fetch({'key', id_user})

        if len(user.items) != 0:
            return user.items[0]

        if len(admin.items) != 0:
            return admin.items[0]
    

#Logout
@both_router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return {'message': 'logout success'}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(both_router)

app.add_middleware(
    CORSMiddleware,
    #allow_origins=['http://app.lemes.my.id', 'https://app.lemes.my.id'],
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

