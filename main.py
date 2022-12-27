from fastapi import FastAPI, HTTPException, APIRouter, Depends, status
# , Security
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya OR using NEXT.js
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from datetime import date, datetime, time
import time as tm
from dateutil.relativedelta import relativedelta

from fastapi.security import OAuth2PasswordRequestForm

# #For deta cron
# from deta import App

# Schemas
from schemas.kolam import *
from schemas.notifikasi import *
from schemas.admin import *
from schemas.beritadanpedoman import *
from schemas.user import *
from utils import *
from schemas.token import TokenSchema
from deps import get_current_user

# Connecting to database
from db import *

# Unicorn
import uvicorn


'''
#Routers
from routers.admin import admin_router
from routers.both import both_router
from routers.user import user_router
'''

# app = App(FastAPI(
#     title="LeMES",
#     version="1.0",
#     prefix="/api"
# ))


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
tags=["user"],
dependencies=[Depends(get_current_user)]
)

#Khusus kolam karena banyak hal yang diinput dari user terkait dengan kolam
kolam_router = APIRouter(
prefix="/kolam",
tags=["kolam"],
dependencies=[Depends(get_current_user)]
)

#Khusus admin
admin_router = APIRouter(
prefix="/admin", 
tags=["admin"]
)

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

@auth_router.post("/signup", summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    res = db_user.fetch([{'username': data.username}, {'email': data.email}])
    if len(res.items) != 0:
        if res.items[0]['username'] == data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already used"
            )
        elif res.items[0]['email'] == data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already used"
            )
    
    new_user = {
        'full_name': data.full_name,
        'email': data.email,
        'username': data.username,
        'hashed_password': get_hashed_password(data.password),
    }

    try:
        validated_new_user = UserDB(**new_user)
        db_user.put(validated_new_user.dict())
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input value"
        )
            
    return validated_new_user.dict()

@auth_router.post("/login", summary="Create access and refresh token", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    req_user = db_user.fetch({'username': form_data.username})
    if len(req_user.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not found"
        )
    
    req_user = req_user.items[0]
    hashed_pass = req_user['hashed_password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong password"
        )
    
    return {
        'access_token': create_access_token(req_user['key']),
        'refresh_token': create_refresh_token(req_user['key'])
    }

@user_router.get("/me", summary="Get logged in user detail", response_model=UserOut)
async def get_me(user: UserOut = Depends(get_current_user)):
    return user

# PR sekarang adalah gambar profile, gambar berita, dan pedoman
# untuk gambar profile nanti dulu
# untuk gambar berita dan pedoman nanti dulu

''''''''''''
#!! KOLAM !!
''''''''''''

# Definisikan fungsi untuk menghitung jumlah pakan harian lele
def hitung_jumlah_pakan(jumlah_lele, berat_lele, kandungan_energi, faktor_konversi, stok_pakan):
    # Hitung berat total lele
    berat_total_lele = jumlah_lele * berat_lele
    # Hitung jumlah pakan yang dibutuhkan dengan rumus yang disebutkan sebelumnya
    jumlah_pakan = (berat_total_lele/ kandungan_energi) * faktor_konversi
    # Jika stok pakan kurang dari jumlah pakan yang dibutuhkan, kembalikan stok pakan sebagai jumlah pakan harian
    if stok_pakan < jumlah_pakan:
        return round(stok_pakan)
    # Jika stok pakan lebih dari atau sama dengan jumlah pakan yang dibutuhkan, kembalikan jumlah pakan yang dibutuhkan sebagai jumlah pakan harian
    else:
        return round(jumlah_pakan)

def waktu_reminder_restock(stok_pakan, jumlah_pakan_harian):
    # Hitung sisa stok pakan setelah 1 hari
    sisa_stok = stok_pakan - jumlah_pakan_harian
    # Jika sisa stok kurang dari 0, maka waktu reminder restock adalah sekarang
    if sisa_stok < 0:
        return datetime.now()
    # Jika sisa stok lebih dari 0, hitung berapa hari lagi stok pakan akan habis
    # dan tambahkan waktu sekarang untuk mendapatkan waktu reminder restock
    else:
        hari_sisa = sisa_stok / jumlah_pakan_harian
        return (datetime.now() + timedelta(days=hari_sisa))

# Waktu reminder restock itu beda dengan panen, kalau restock its all about pakan, kalau panen its all about waktu panen
# Definisikan fungsi untuk menentukan waktu reminder panen
def waktu_panen(jumlah_pakan_harian, lama_panen, waktu_panen_input):
    # Hitung jumlah hari yang diperlukan untuk panen
    jumlah_hari_panen = lama_panen / jumlah_pakan_harian
    # Hitung waktu reminder panen dengan menambahkan jumlah hari yang diperlukan untuk panen pada waktu panen
    waktu_panen = waktu_panen_input + timedelta(days=jumlah_hari_panen)
    # Kembalikan waktu reminder panen dalam format YYYY-MM-DD HH:MM:SS
    return waktu_panen

#takaranlele
@kolam_router.post("/inputdata", summary="Mengukur Tarakan Lele")
def insert_hitung_jumlah_pakan(kolam: KolamIn, user: UserOut = Depends(get_current_user)):
    req_kolam_user = db_kolam.fetch({'nama_kolam': (kolam.nama_kolam).lower(), 'username': user.username})

    if len(req_kolam_user.items) != 0:
        raise HTTPException(
            status_code=400,
            detail="Data already exist"
        )
    
    waktu_panen_result = waktu_panen(hitung_jumlah_pakan(kolam.jumlah_lele, kolam.berat_lele, 3.5, 0.5, kolam.stock_pakan), 60, (date.today() + relativedelta(months=+2)))

    insert_kolam = {
        "username": user.username,
        "key": str(int(generateKey(tm.time() * 10000))),
        "nama_kolam": (kolam.nama_kolam).lower(), 
        "jumlah_lele": kolam.jumlah_lele,
        "berat_lele": kolam.berat_lele,
        "stock_pakan": kolam.stock_pakan,
        "waktu_tebar": datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
        "jumlah_pakan_harian": hitung_jumlah_pakan(kolam.jumlah_lele, kolam.berat_lele, 3.5, 0.5, kolam.stock_pakan),
        "waktu_panen": waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_restock": None
    }

    try:
        validated_new_kolam = KolamDB(**insert_kolam)
        db_kolam.put(validated_new_kolam.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    # Meng-push ke notifikasiIn

    # Ini untuk notifikasi sehari 3 kali
    inputNotifikasiHarian = {
        "username": user.username,
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "Harian",
        "waktu" : "Pagi",
        "waktu_masuk": date.today().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_keluar": (date.today() + relativedelta(days=+1)).strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_habis": (date.today() + relativedelta(days=+30)).strftime("%m/%d/%Y, %H:%M:%S")
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
        "username": user.username,
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "Panen",
        "waktu": "H-2",
        "waktu_masuk": date.today().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_keluar": waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_habis": (waktu_panen_result + relativedelta(months=+2, days=+6)).strftime("%m/%d/%Y, %H:%M:%S")
    }

    try:
        validated_new_notificationpanen = inputNotifikasi(**inputNotifikasiPanen)
        db_notifikasiIn.put(validated_new_notificationpanen.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    return insert_kolam

@kolam_router.post("/inputdatarestock", summary="Merestock pakan lele", response_model=RestockOut)
def menghitung_restock(nama_kolam: str, user: UserOut = Depends(get_current_user)):
    req_restock = db_kolam.fetch({'nama_kolam': (nama_kolam).lower(), 'username': user.username})

    if len(req_restock.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )

    assign_restock = req_restock.items[0]
    stock_pakan_restock = assign_restock['stock_pakan']
    jumlah_pakan_harian_restock = assign_restock['jumlah_pakan_harian']

    waktu_reminder_restock_result = waktu_reminder_restock(stock_pakan_restock, jumlah_pakan_harian_restock)
    
    update = {
        "waktu_restock": waktu_reminder_restock_result.strftime("%m/%d/%Y, %H:%M:%S"),
    }
    
    db_kolam.update(update, assign_restock['key'])

    # Ini untuk notifikasi restock

    # Kayanya sih buat beberapa kondisi, most likely it would be six conditions with different ones

    inputNotifikasiRestock = {
        "username": user.username,
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "Restock",
        "waktu_masuk" : date.today().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_keluar" : waktu_reminder_restock_result.strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_habis" : (waktu_reminder_restock_result + relativedelta(days=+2)).strftime("%m/%d/%Y, %H:%M:%S")
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
def info_kolam(user: UserOut = Depends(get_current_user)):
    res_kolam = db_kolam.fetch({'username': user.username})
    all_items = res_kolam.items

    if len(all_items) == 0:
            raise HTTPException(
            status_code=400,
            detail="Tidak ada data kolam"
        )

    return all_items

# delete kolam, tergantung nama kolamnya
@kolam_router.delete("/delete/", summary="Menghapus Kolam")
def delete_kolam(nama_kolam: str, user: UserOut = Depends(get_current_user)):
    req_kolam = db_kolam.fetch({'nama_kolam': (nama_kolam).lower(), 'username': user.username})
    db_kolam.delete(req_kolam.items[0]['key'])

    return {'message': 'success', 'nama_kolam': nama_kolam}

# search
@kolam_router.get("/info/{nama_kolam}", summary="Mencari Kolam")
def search(nama_kolam: str, user: UserOut = Depends(get_current_user)):
    req_search = db_kolam.fetch({'nama_kolam': (nama_kolam).lower(), 'username': user.username})
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
# @app.lib.cron()
@app.get("/proses_notifikasi", summary="Notifikasi", include_in_schema=False)
def proses_notifikasi(e = None):
    inT1 = time(8, 00, 00)
    inT2 = time(12, 00, 00)
    inT3 = time(17, 00, 00)

    outT1 = time(9, 00, 00)
    outT2 = time(13, 00, 00)
    outT3 = time(18, 00, 00)

    inPagi = datetime.combine(date.today(), inT1)
    inSiang = datetime.combine(date.today(), inT2)
    inSore = datetime.combine(date.today(), inT3)
    outPagi = datetime.combine(date.today(), outT1)
    outSiang = datetime.combine(date.today(), outT2)
    outSore = datetime.combine(date.today(), outT3)

    # we have to make new row first ig
    # so this is just put the data to the database

    # this is for panen
    # bisa diakalin lewat kondisi ini jadi for-nya 
    notif_resHarian = db_notifikasiIn.fetch({"tipe":"Harian"})
    all_itemsHarian = notif_resHarian.items
    
    notif_resPanen = db_notifikasiIn.fetch({"tipe":"Panen"})
    all_itemsPanen = notif_resPanen.items

    notif_resRestock = db_notifikasiIn.fetch({"tipe":"Restock"})
    all_itemsRestock = notif_resRestock.items

    # filter dari notifikasiOut dan masuk key dari notifikasiIn ke notifikasiOut dengan variabel keyIn, nah terus jika sama jangan dimasukin lagi
    # dan mungkin bisa juga ditambah kondisi pagi, siang, sore

    for i in range(0, len(all_itemsHarian)):
        # Ini untuk notifikasi harian
        if (date.today() >= datetime.strptime((all_itemsHarian[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and date.today() <= datetime.strptime((all_itemsHarian[i]['waktu_habis']), "%m/%d/%Y, %H:%M:%S").date()):
            if (datetime.now() >= inPagi and datetime.now() <= outPagi and all_itemsHarian[i]['waktu'] == "Pagi"):
                outputNotifikasiHarian = {
                    "key": str(int(generateKey(tm.time() * 10000))),
                    "username": all_itemsHarian[i]['username'],
                    "tipe": "Harian",
                    "waktu": "Pagi",
                    "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "messages" : "Reminder untuk memberi pakan pada Pagi hari!"
                }
                db_notifikasiOut.put(outputNotifikasiHarian)
                notifikasi_update = {
                    "waktu": "Siang"
                }
                db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
            elif (datetime.now() >= inSiang and datetime.now() <= outSiang and all_itemsHarian[i]['waktu'] == "Siang"):
                outputNotifikasiHarian = {
                    "username": all_itemsHarian[i]['username'],
                    "key": str(int(generateKey(tm.time() * 10000))),
                    "tipe": "Harian",
                    "waktu": "Siang",
                    "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "messages" : "Reminder untuk memberi pakan pada Siang hari!"
                }
                db_notifikasiOut.put(outputNotifikasiHarian)
                notifikasi_update = {
                    "waktu": "Sore"
                }
                db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
            elif (datetime.now() >= inSore and datetime.now() <= outSore and all_itemsHarian[i]['waktu'] == "Sore"):
                outputNotifikasiHarian = {
                    "username": all_itemsHarian[i]['username'],
                    "key": str(int(generateKey(tm.time() * 10000))),
                    "tipe": "Harian",
                    "waktu": "Sore",
                    "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    "messages" : "Reminder untuk memberi pakan pada Sore hari!"
                }
                db_notifikasiOut.put(outputNotifikasiHarian)
                notifikasi_update = {
                    "waktu": "Pagi"
                }
                db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
            elif (datetime.now() >= outSore):
                notifikasi_nitip = all_itemsHarian[i]
                db_notifikasiIn.delete(all_itemsHarian[i]['key'])

                # Ini untuk notifikasi sehari 3 kali
                # Bakal ada user tapi entah di mana
                inputNotifikasiHarian = {
                    "username": notifikasi_nitip['username'],
                    "key": str(int(generateKey(tm.time() * 10000))),
                    "tipe": "Harian",
                    "waktu": notifikasi_nitip['waktu'],
                    "waktu_masuk": notifikasi_nitip['waktu_masuk'],
                    "waktu_keluar": (date.today() + relativedelta(days=+1)).strftime("%m/%d/%Y, %H:%M:%S"),
                    "waktu_habis": notifikasi_nitip['waktu_habis'],
                }

                try:
                    validated_new_notificationharian = inputNotifikasi(**inputNotifikasiHarian)
                    db_notifikasiIn.put(validated_new_notificationharian.dict())
                except ValidationError:
                    raise HTTPException(
                        status_code=404,
                        detail="Invalid input value"
                    )

    # untuk yang di bawah malah better kalau dilock
    for i in range(0, len(all_itemsPanen)):        
        # Ini untuk notifkasi panen
        if (date.today() >= datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and date.today() <= datetime.strptime((all_itemsPanen[i]['waktu_habis']), "%m/%d/%Y, %H:%M:%S").date()):
            if (date.today() == datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date()) :
                if (datetime.now() >= datetime.combine(date.today(), time(10, 1, 00)) and datetime.now() <= datetime.combine(date.today(), time(11, 2, 00))) and all_itemsPanen[i]['waktu'] == "H-2":
                    outputNotifikasiPanen = {
                        "username": all_itemsPanen[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Panen",
                        "waktu": "H-2",
                        "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-2 Sebelum Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    notifikasi_update = {
                        "waktu": "H-1"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])
            elif (date.today() == datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() + relativedelta(days=+1)):
                if (datetime.now() >= datetime.combine(date.today(), time(10, 1, 00)) and datetime.now() <= datetime.combine(date.today(), time(11, 2, 00))) and all_itemsPanen[i]['waktu'] == "H-1":
                    outputNotifikasiPanen = {
                        "username": all_itemsPanen[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Panen",
                        "waktu": "H-1",
                        "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-1 Sebelum Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    notifikasi_update = {
                        "waktu": "H-Day"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])
            elif (date.today() == datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() + relativedelta(days=+2)) and all_itemsPanen[i]['waktu'] == "H-Day":
                if (datetime.now() >= datetime.combine(date.today(), time(10, 1, 00)) and datetime.now() <= datetime.combine(date.today(), time(11, 00, 00))):
                    outputNotifikasiPanen = {
                        "username": all_itemsPanen[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Panen",
                        "waktu": "H-Day",
                        "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Waktunya Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    notifikasi_update = {
                        "waktu": "Done"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])

    for i in range(0, len(all_itemsRestock)):
        # Ini untuk notifikasi restock
        if (date.today() >= datetime.strptime((all_itemsRestock[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and date.today() <= datetime.strptime((all_itemsRestock[i]['waktu_habis']), "%m/%d/%Y, %H:%M:%S").date()):
            if (date.today() == datetime.strptime((all_itemsRestock[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() ):
                if (datetime.now() >= datetime.combine(date.today(), time(10, 2, 00)) and datetime.now() <= datetime.combine(date.today(), time(11, 3, 00)) and all_itemsRestock[i]['waktu'] == "H-1"):
                    outputNotifikasiRestock = {
                        "username": all_itemsRestock[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Restock",
                        "waktu": "H-1",
                        "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-1 Sebelum Restock Pakan!"
                    }
                    db_notifikasiOut.put(outputNotifikasiRestock)
                    notifikasi_update = {
                        "waktu": "H-Day"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])
            elif (date.today() == datetime.strptime((all_itemsRestock[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date()  + relativedelta(days=+1)):
                if (datetime.now() >= datetime.combine(date.today(), time(10, 2, 00)) and datetime.now() <= datetime.combine(date.today(), time(11, 3, 00)) and all_itemsRestock[i]['waktu'] == "H-Day"):
                    outputNotifikasiRestock = {
                        "username": all_itemsRestock[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "tipe": "Restock",
                        "waktu": "H-Day",
                        "waktu_keluar" : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Waktunya Restock Pakan!"
                    }
                    db_notifikasiOut.put(outputNotifikasiRestock)
                    notifikasi_update = {
                        "waktu": "Done"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])

    # This is for return the value that in db, all of values
    res_out_notifikasi = db_notifikasiOut.fetch()
    
    return res_out_notifikasi.items

@user_router.get("/notifikasi", summary="Get Notifikasi")
def get_notifikasi(user: UserOut = Depends(get_current_user)):
    res_out_notifikasi = db_notifikasiOut.fetch({'username': user.username});
    return res_out_notifikasi.items

''''''''''''
#!! ADMIN !!
''''''''''''

#admin - berita
@admin_router.post("/post/berita", response_model=BeritaDanPedomanDB)
def post_berita(berita: BeritaDanPedomanIn):
    berita = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "berita",
        "judul_berita_dan_pedoman": berita.judul_berita_dan_pedoman,
        "tanggal_berita_dan_pedoman": berita.tanggal_berita_dan_pedoman,
        "isi_berita_dan_pedoman": berita.isi_berita_dan_pedoman,
        "file_berita_dan_pedoman": berita.file_berita_dan_pedoman
    }
    return db_beritadanpedoman.put(berita)

#admin - pedoman
@admin_router.post("/post/pedoman", response_model=BeritaDanPedomanDB)
def post_Pedoman(pedoman: BeritaDanPedomanIn):
    pedoman = {
        "key": str(int(generateKey(tm.time() * 10000))),
        "tipe": "pedoman",
        "judul_berita_dan_pedoman": pedoman.judul_berita_dan_pedoman,
        "tanggal_berita_dan_pedoman": pedoman.tanggal_berita_dan_pedoman,
        "isi_berita_dan_pedoman": pedoman.isi_berita_dan_pedoman,
        "file_berita_dan_pedoman": pedoman.file_berita_dan_pedoman
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
@admin_router.delete("/delete/beritadanpedoman")
def delete_pedomanklik(beritadanpedoman_id: str):
    req_pedoman = db_beritadanpedoman.fetch({"key": beritadanpedoman_id})
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
    return req_berita.items

#Pedoman
@beritapedoman_router.get("/pedoman")
def pedoman():
    req_pedoman = db_beritadanpedoman.fetch({"tipe": "pedoman"})
    if len(req_pedoman.items) == 0:
        raise HTTPException(
        status_code=400,
        detail="Laman Pedoman Kosong"
        )
    return req_pedoman.items

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

