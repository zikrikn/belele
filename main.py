from fastapi import FastAPI, HTTPException, APIRouter, Security
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya OR using NEXT.js
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from datetime import date, datetime, time
import time as tm
from dateutil.relativedelta import relativedelta

#For deta cron
from deta import App

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

app = App(FastAPI(
    title="LeMES",
    version="1.0",
    prefix="/api"
))

# app = FastAPI(
#     title="LeMES",
#     version="1.0",
#     prefix="/api"
# )

#fungsi untuk generate key agar lastest record muncul paling atas
def generateKey(timestap):
    bigNumber = 8.64e15
    return (bigNumber - timestap)

@app.get("/", include_in_schema=False)
def redirect_docs():
    return RedirectResponse("/docs")

#Untuk keamanan
auth_router = APIRouter(
prefix="/auth",
tags=["auth"]
)

#Khusus user biasa
user_router = APIRouter(
prefix="/user",
tags=["user"]
)

#Khusus kolam karena banyak hal yang diinput dari user terkait dengan kolam
kolam_router = APIRouter(
prefix="/kolam",
tags=["kolam"]
)

#Khusus admin
admin_router = APIRouter(
prefix="/admin", 
tags=["admin"])

#Khusus untuk berita termasuk memasukan berita dan menampilkan berita
beritapedoman_router = APIRouter(
prefix="/beritapedoman",
tags=["berita_pedoman"]
)

''''''''''''
#!! AUTH !!
''''''''''''

#Membuat auth untuk login dan signup
#!!!Tambahannya signup admin dan delete akun!!!

@auth_router.post('/signup')
def signup(user_details: PemberiPakanDB):
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
def login(user_details: PemberiPakanIn):
    user = db_pemberipakan.get(user_details.key)
    if (user is None):
        return HTTPException(status_code=401, detail='Invalid username')
    if (not auth_handler.verify_password(user_details.PasswordPP, user['password'])):
        return HTTPException(status_code=401, detail='Invalid password')
    
    access_token = auth_handler.encode_token(user['key'])
    refresh_token = auth_handler.encode_refresh_token(user['key'])
    return {'access_token': access_token, 'refresh_token': refresh_token}

@auth_router.get('/refresh_token')
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token}


# @auth_router.post('/secret')
# def secret_data(credentials: HTTPAuthorizationCredentials = Security(security)):
#     token = credentials.credentials
#     if(auth_handler.decode_token(token)):
#         return 'Top Secret data only authorized users can access this info'

# @auth_router.get('/notsecret')
# def not_secret_data():
#     return 'Not secret data'

''''''''''''
#!! KOLAM !!
''''''''''''
# https://stackoverflow.com/questions/4170655/how-to-convert-a-datetime-string-back-to-datetime-object
#takaranlele
@kolam_router.post("/inputdata", summary="Mengukur Tarakan Lele", response_model=KolamIn)
def takaran_leleIn(newKolam: KolamIn):
    req_kolam = db_kolam.fetch({'NamaKolam': (newKolam.NamaKolam).lower()})
    if len(req_kolam.items) != 0:
        raise HTTPException(
            status_code=400,
            detail="Data already exist"
        )

    kolam = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "NamaKolam": (newKolam.NamaKolam).lower(), 
        "JumlahLele": newKolam.JumlahLele,
        "BeratLele": newKolam.BeratLele,
        "TanggalAwalTebarBibit": newKolam.TanggalAwalTebarBibit,
        "TakaranPangan": 0,
        "JumlahPakan": 0,
        "RestockPakan": 0
    }

    hasiljumlah = newKolam.BeratLele * (3/100)
    print(hasiljumlah)
    kolam['TakaranPangan'] = hasiljumlah

    try:
        validated_new_profile = KolamDB(**kolam)
        db_kolam.put(validated_new_profile.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    # Meng-push ke notifikasiIn

    # Ini untuk notifikasi sehari 3 kali
    inputNotifikasiHarian = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "Harian",
        "waktuMasuk" : date.today().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktuKeluar" : (date.today() + relativedelta(days=+1)).strftime("%m/%d/%Y, %H:%M:%S"),
        "waktuHabis" : (date.today() + relativedelta(days=+30)).strftime("%m/%d/%Y, %H:%M:%S")
    }

    try:
        validated_new_notificationharian = inputNotifikasi(**inputNotifikasiHarian)
        db_notifikasiIn.put(validated_new_notificationharian.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    # Ini untuk notifikasi panen
    inputNotifikasiPanen = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "Panen",
        "waktuMasuk" : date.today().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktuKeluar" : (date.today() + relativedelta(months=+2)).strftime("%m/%d/%Y, %H:%M:%S"),
        "waktuHabis" : (date.today() + relativedelta(months=+2, days=+6)).strftime("%m/%d/%Y, %H:%M:%S")
    }

    try:
        validated_new_notificationpanen = inputNotifikasi(**inputNotifikasiPanen)
        db_notifikasiIn.put(validated_new_notificationpanen.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    return kolam

@kolam_router.post("/inputdatarestock", summary="Merestock pakan lele", response_model=RestockOut)
def menghitung_restock(newRestock: RestockIn):
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

    # Ini untuk notifikasi restock

    # Kayanya sih buat beberapa kondisi, most likely it would be six conditions with different ones

    hariRestock = 20

    inputNotifikasiRestock = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "Restock",
        "waktuMasuk" : date.today().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktuKeluar" : (date.today() + relativedelta(days=+hariRestock)).strftime("%m/%d/%Y, %H:%M:%S"), 
        "waktuHabis" : (date.today() + relativedelta(days=+hariRestock) + relativedelta(days=+2)).strftime("%m/%d/%Y, %H:%M:%S")
    }

    try:
        validated_new_notificationrestock = inputNotifikasi(**inputNotifikasiRestock)
        db_notifikasiIn.put(validated_new_notificationrestock.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    return assign_restock

# get info all kolam
@kolam_router.get("/info/all", summary="Melihat Info Kolam")
def info_kolam():
    res_kolam = db_kolam.fetch()
    all_items = res_kolam.items

    if len(all_items) == 0:
            raise HTTPException(
            status_code=400,
            detail="Tidak ada data kolam"
        )

    return all_items

# delete kolam
@kolam_router.delete("/delete/{keykolam}", summary="Menghapus Kolam")
def delete_kolam(keykolam: str):
    req_kolam = db_kolam.get(keykolam)
    namakolam = req_kolam['NamaKolam']
    db_kolam.delete(req_kolam['key'])

    return {'message': 'success', 'namakolam': namakolam}

# search
@kolam_router.get("/info/{something}")
def search(something: str):
    req_search = db_kolam.fetch({'NamaKolam': (something).lower()}) #use fixed query
    if len(req_search.items) == 0:
            raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )

    return req_search.items

''''''''''''
#!! USER !!
''''''''''''

#notifikasi //buat trigger atau gak refresh setiap berapa menit sekali //atau tentukan waktu untuk trigger
@app.lib.cron()
@user_router.get("/notifikasi")
def notifikasi(e = None):
    inT1 = time(8, 00, 00)
    inT2 = time(12, 00, 00)
    inT3 = time(17, 00, 00)

    outT1 = time(8, 1, 00)
    outT2 = time(12, 1, 00)
    outT3 = time(17, 1, 00)

    inPagi = datetime.combine(date.today(), inT1)
    inSiang = datetime.combine(date.today(), inT2)
    inSore = datetime.combine(date.today(), inT3)
    outPagi = datetime.combine(date.today(), outT1)
    outSiang = datetime.combine(date.today(), outT2)
    outSore = datetime.combine(date.today(), outT3)

    #we have to make new row first ig
    #so this is just put the data to the database

    #this is for panen
    #bisa diakalin lewat kondisi ini jadi for-nya 
    notif_resHarian = db_notifikasiIn.fetch({"tipe":"Harian"})
    all_itemsHarian = notif_resHarian.items
    
    notif_resPanen = db_notifikasiIn.fetch({"tipe":"Panen"})
    all_itemsPanen = notif_resPanen.items

    notif_resRestock = db_notifikasiIn.fetch({"tipe":"Restock"})
    all_itemsRestock = notif_resRestock.items

    for i in range(0, len(all_itemsHarian)):
        #Ini untuk notifikasi harian
        if (date.today() >= datetime.strptime((all_itemsHarian[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and date.today() <= datetime.strptime((all_itemsHarian[i]['waktuHabis']), "%m/%d/%Y, %H:%M:%S").date()):
            if (datetime.now() >= inPagi and datetime.now() <= outPagi):
                outputNotifikasiHarian = {
                    "key": str(int(generateKey(tm.time() * 10000))),
                    "tipe": "Harian",
                    "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "messages" : "Reminder untuk memberi pakan pada Pagi hari!"
                }
                db_notifikasiOut.put(outputNotifikasiHarian)
                tm.sleep(60)
            elif (datetime.now() >= inSiang and datetime.now() <= outSiang):
                outputNotifikasiHarian = {
                    "key": str(int(generateKey(tm.time() * 10000))),
                    "tipe": "Harian",
                    "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "messages" : "Reminder untuk memberi pakan pada Siang hari!"
                }
                db_notifikasiOut.put(outputNotifikasiHarian)
                tm.sleep(60)
            elif (datetime.now() >= inSore and datetime.now() <= outSore):
                outputNotifikasiHarian = {
                    "key": str(int(generateKey(tm.time() * 10000))),
                    "tipe": "Harian",
                    "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "messages" : "Reminder untuk memberi pakan pada Sore hari!"
                }
                db_notifikasiOut.put(outputNotifikasiHarian)
                tm.sleep(60)

    for i in range(0, len(all_itemsPanen)):        
        #Ini untuk notifkasi panen
        if (date.today() >= datetime.strptime((all_itemsPanen[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and date.today() <= datetime.strptime((all_itemsPanen[i]['waktuHabis']), "%m/%d/%Y, %H:%M:%S").date()):
            if (date.today() == datetime.strptime((all_itemsPanen[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date()) :
                if (datetime.now() >= datetime.combine(date.today(), time(10, 1, 00)) and datetime.now() <= datetime.combine(date.today(), time(10, 2, 00))):
                    outputNotifikasiPanen = {
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Panen",
                        "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-2 Sebelum Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    tm.sleep(60)
            elif (date.today() == datetime.strptime((all_itemsPanen[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date() + relativedelta(days=+2)):
                if (datetime.now() >= datetime.combine(date.today(), time(12, 1, 00)) and datetime.now() <= datetime.combine(date.today(), time(12, 2, 00))):
                    outputNotifikasiPanen = {
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Panen",
                        "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-1 Sebelum Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    tm.sleep(60)
            elif (date.today() == datetime.strptime((all_itemsPanen[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date() + relativedelta(days=+3)):
                if (datetime.now() >= datetime.combine(date.today(), time(17, 1, 00)) and datetime.now() <= datetime.combine(date.today(), time(10, 2, 00))):
                    outputNotifikasiPanen = {
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Panen",
                        "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Waktunya Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    tm.sleep(60)

    for i in range(0, len(all_itemsRestock)):
        #Ini untuk notifikasi restock
        if (date.today() >= datetime.strptime((all_itemsRestock[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and date.today() <= datetime.strptime((all_itemsRestock[i]['waktuHabis']), "%m/%d/%Y, %H:%M:%S").date()):
            if (date.today() == datetime.strptime((all_itemsRestock[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date() ):
                if (datetime.now() >= datetime.combine(date.today(), time(10, 2, 00)) and datetime.now() <= datetime.combine(date.today(), time(10, 3, 00))):
                    outputNotifikasiRestock = {
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Restock",
                        "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-1 Sebelum Restock Pakan!"
                    }
                    db_notifikasiOut.put(outputNotifikasiRestock)
                    tm.sleep(60)
            elif (date.today() == datetime.strptime((all_itemsRestock[i]['waktuKeluar']), "%m/%d/%Y, %H:%M:%S").date()  + relativedelta(days=+1)):
                if (datetime.now() >= datetime.combine(date.today(), time(12, 2, 00)) and datetime.now() <= datetime.combine(date.today(), time(10, 3, 00))):
                    outputNotifikasiRestock = {
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Restock",
                        "waktuKeluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Waktunya Restock Pakan!"
                    }
                    db_notifikasiOut.put(outputNotifikasiRestock)
                    tm.sleep(60)

    #this is for return the value that in db, all of values
    res_out_notifikasi = db_notifikasiOut.fetch();
    
    return res_out_notifikasi.items

#profile admin - user
@user_router.get("/profile/{id_user}")
def profile(id_user: str):
        user = db_pemberipakan.fetch({'key': id_user})
        admin = db_admin.fetch({'key', id_user})

        if len(user.items) != 0:
            return user.items[0]

        if len(admin.items) != 0:
            return admin.items[0]

#Logout
@user_router.post("/logout")
def logout():
    return {'message': 'logout success'}

''''''''''''
#!! ADMIN !!
''''''''''''

#admin - berita
@admin_router.post("/post/berita", response_model=BeritaDanPedomanDB)
def post_berita(berita: BeritaDanPedomanIn):

    berita = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "berita",
        "judulBeritaDanPedoman": berita.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": berita.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": berita.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": berita.fileBeritaDanPedoman
    }
    return db_beritadanpedoman.put(berita)

#admin - pedoman
@admin_router.post("/post/pedoman", response_model=BeritaDanPedomanDB)
def post_Pedoman(pedoman: BeritaDanPedomanIn):

    pedoman = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "pedoman",
        "judulBeritaDanPedoman": pedoman.judulBeritaDanPedoman,
        "tanggalBeritaDanPedoman": pedoman.tanggalBeritaDanPedoman,
        "isiBeritaDanPedoman": pedoman.isiBeritaDanPedoman,
        "fileBeritaDanPedoman": pedoman.fileBeritaDanPedoman
    }
    return db_beritadanpedoman.put(pedoman)

#admin - delete berita //nanti pakai key-nya untuk menghapus
@admin_router.delete("/delete/berita")
def delete_berita():
    req_berita = db_beritadanpedoman.fetch({"tipe": "berita"})
    db_beritadanpedoman.delete(req_berita.items[0]['key'])
    return {'message': 'success'}

# admin - delete pedoman - the lastest 
# maybe we can changes this into by "key"
@admin_router.delete("/delete/pedoman")
def delete_pedoman():
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    db_beritadanpedoman.delete(req_pedoman.items[0]['key'])
    return {'message': 'success'}

# untuk menghapus pedoman dengan klik lewat trigger kunci-nya yang bakal dilihat kunci-nya dari artikel yang sedang dilihat
@admin_router.delete("/delete/pedoman-byclick")
def delete_pedomanklik(kunci: BeritaDanPedomanDB):
    req_pedoman = db_beritadanpedoman.fetch({"key": kunci})
    db_beritadanpedoman.delete(req_pedoman.items[0]['key'])
    return {'message': 'success'}


''''''''''''
#!! BERITA DAN PEDOMAN !!
''''''''''''

#Berita
@beritapedoman_router.get("/berita")
def berita():
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
@beritapedoman_router.get("/pedoman")
def pedoman():
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    if len(req_pedoman.items) == 0:
        raise HTTPException(
        status_code=400,
        detail="Laman Berita Kosong"
        )
    
    isipedoman = req_pedoman.items
    return isipedoman

app.include_router(auth_router, tags=["auth"])
app.include_router(user_router, tags=["user"])
app.include_router(kolam_router, tags=["kolam"])
app.include_router(admin_router, tags=["admin"])
app.include_router(beritapedoman_router, tags=["berita_pedoman"])

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

