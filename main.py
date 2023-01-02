# FastAPI Library
from fastapi import FastAPI, HTTPException, APIRouter, Depends, status, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
# Schemas
from schemas.kolam import *
from schemas.notifikasi import *
from schemas.beritadanpedoman import *
from schemas.user import *
# Security
from fastapi.security import OAuth2PasswordRequestForm
from utils import *
from schemas.token import TokenSchema
from deps import get_current_user
# Connecting to Database
from db import *
# Connecting to Drive
from drive import *
# Unicorn
# import uvicorn
# Others Libary
from pydantic import ValidationError
from datetime import datetime, time, tzinfo, timedelta
from dateutil.relativedelta import relativedelta
import time as tm
import random
import string
import pytz

# Deta Cron
# from deta import App

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

# Generate key to make the lastest record on the top.
def generateKey(timestap):
    bigNumber = 8.64e15
    return (bigNumber - timestap)

# Generate a random string of ASCII characters.
def generate_id(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))

# Menentukan timezone Indonesia Barat
tz = pytz.timezone('Asia/Jakarta')
class TZ(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=7)

tz_py2 = TZ() # untk melakukan return detatime in Python 2

@app.get("/", include_in_schema=False)
def redirect_docs():
    return RedirectResponse("/docs")

# Untuk keamanan
auth_router = APIRouter(
prefix="/auth",
tags=["auth"]
)

# Khusus user biasa
user_router = APIRouter(
prefix="/user",
tags=["user"],
dependencies=[Depends(get_current_user)]
)

# Khusus kolam karena banyak hal yang diinput dari user terkait dengan kolam
kolam_router = APIRouter(
prefix="/kolam",
tags=["kolam"],
dependencies=[Depends(get_current_user)]
)

# Khusus admin
admin_router = APIRouter(
prefix="/admin", 
tags=["admin"]
)

# Khusus untuk berita termasuk memasukan berita dan menampilkan berita
beritapedoman_router = APIRouter(
prefix="/beritapedoman",
tags=["berita_pedoman"]
)

''''''''''''
# !! AUTH !!
''''''''''''

# Membuat auth untuk login dan signup
# !!!Tambahannya signup admin dan delete akun!!!

@auth_router.post("/signup", summary="Create New User", response_model=UserOut)
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
        'photoprofile': None
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

@auth_router.post("/login", summary="Create Access and Refresh Token", response_model=TokenSchema)
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

@user_router.get("/profile", response_model=ProfileOut)
async def get_profil(user: UserOut = Depends(get_current_user)):
    req_profil = db_user.fetch({'username': user.username})
    if len(req_profil.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return req_profil.items[0]

# Return a file from the storage Drive.
@app.get("/cdn/{id}", tags=["CDN"], summary="CDN")
async def cdn(id: str):
    file = drive_photoprofile.get(id)
    if file is None:
        raise HTTPException(status_code=404)
    headers = {"Cache-Control": "public, max-age=86400"}
    return StreamingResponse(file.iter_chunks(4096), media_type="image/jpg", headers=headers)

@user_router.post("/upload_photoprofile", response_model=ProfileOut, summary="Upload Photo Profile")
async def upload_photo_profile(request: Request, img: UploadFile, user: UserOut = Depends(get_current_user)):
    req_user = db_user.fetch({'username': user.username})

    if len(req_user.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data not exist"
        )

    id = generate_id()
    file_content = await img.read()
    file_name = f"{id}_{user.username}.jpg"
    drive_photoprofile.put(file_name, file_content)
    
    update = {
        'photoprofile': f"{request.base_url}cdn/{file_name}"
    }

    update_photoprofile = req_user.items[0]
    update_photoprofile['photoprofile'] = f"{request.base_url}cdn/{file_name}"
    db_user.update(update, update_photoprofile['key'])
    
    return update_photoprofile

''''''''''''
#!! KOLAM !!
''''''''''''

# Fungsi untuk menghitung jumlah pakan harian lele
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
        return datetime.now(tz).date()
    # Jika sisa stok lebih dari 0, hitung berapa hari lagi stok pakan akan habis
    # dan tambahkan waktu sekarang untuk mendapatkan waktu reminder restock
    else:
        hari_sisa = sisa_stok / jumlah_pakan_harian
        return (datetime.now(tz).date() + timedelta(days=hari_sisa))

# Waktu reminder restock itu beda dengan panen
# Definisikan fungsi untuk menentukan waktu reminder panen
def waktu_panen(jumlah_pakan_harian, lama_panen, waktu_panen_input):
    # Hitung jumlah hari yang diperlukan untuk panen
    jumlah_hari_panen = lama_panen / jumlah_pakan_harian
    # Hitung waktu reminder panen dengan menambahkan jumlah hari yang diperlukan untuk panen pada waktu panen
    waktu_panen = waktu_panen_input + timedelta(days=jumlah_hari_panen)
    # Kembalikan waktu reminder panen dalam format YYYY-MM-DD HH:MM:SS
    return waktu_panen

@kolam_router.post("/inputdata", summary="Mengukur Jumlah Pakan Harian Lele")
def insert_hitung_jumlah_pakan(kolam: KolamIn, user: UserOut = Depends(get_current_user)):
    req_kolam_user = db_kolam.fetch({'nama_kolam': (kolam.nama_kolam).lower(), 'username': user.username})

    if len(req_kolam_user.items) != 0:
        raise HTTPException(
            status_code=400,
            detail="Data already exist"
        )
    
    waktu_panen_result = waktu_panen(hitung_jumlah_pakan(kolam.jumlah_lele, kolam.berat_lele, 3.5, 0.5, kolam.stock_pakan), 60, (datetime.now(tz).date()+ relativedelta(months=+2)))

    insert_kolam = {
        "username": user.username,
        "key": str(int(generateKey(tm.time() * 10000))),
        "nama_kolam": (kolam.nama_kolam).lower(), 
        "jumlah_lele": kolam.jumlah_lele,
        "berat_lele": kolam.berat_lele,
        "stock_pakan": kolam.stock_pakan,
        "waktu_tebar": datetime.now(tz).astimezone(tz).strftime('%m/%d/%Y, %H:%M:%S'),
        "jumlah_pakan_harian": hitung_jumlah_pakan(kolam.jumlah_lele, kolam.berat_lele, 3.5, 0.5, kolam.stock_pakan),
        "waktu_panen": waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_restock": None,
        "allow_restock_ulang": False
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

    # Di lokal aman, di server error

    # inT1 = time(17, 00, 1)
    # inT2 = time(8, 00, 1)
    # inT3 = time(12, 00, 1)

    # outT1 = time(8, 00, 00)
    # outT2 = time(12, 00, 00)
    # outT3 = time(17, 00, 00)

    # inPagi = datetime.combine(datetime.now().date(), inT1).replace(tzinfo=tz_py2) + relativedelta(days=-1)
    # inSiang = datetime.combine(datetime.now().date(), inT2).replace(tzinfo=tz_py2)
    # inSore = datetime.combine(datetime.now().date(), inT3).replace(tzinfo=tz_py2)
    # outPagi = datetime.combine(datetime.now().date(), outT1).replace(tzinfo=tz_py2)
    # outSiang = datetime.combine(datetime.now().date(), outT2).replace(tzinfo=tz_py2)
    # outSore = datetime.combine(datetime.now().date(), outT3).replace(tzinfo=tz_py2)

    # # Ini untuk notifikasi sehari 3 kali

    # # Ini masih bugs
    # if (datetime.now().replace(tzinfo=tz_py2) >= inPagi and datetime.now().replace(tzinfo=tz_py2) <= outPagi):
    #     inputNotifikasiHarian = {
    #         "username": user.username,
    #         "key": str(int(generateKey(tm.time() * 10000))),
    #         "nama_kolam": (kolam.nama_kolam).lower(),
    #         "tipe": "Harian",
    #         "waktu" : "Pagi",
    #         "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_habis": waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S")
    #     }
    #     db_notifikasiIn.put(inputNotifikasiHarian)
    # elif (datetime.now().replace(tzinfo=tz_py2) >= inSiang and datetime.now().replace(tzinfo=tz_py2) <= outSiang):
    #     inputNotifikasiHarian = {
    #         "username": user.username,
    #         "key": str(int(generateKey(tm.time() * 10000))),
    #         "nama_kolam": (kolam.nama_kolam).lower(),
    #         "tipe": "Harian",
    #         "waktu" : "Siang",
    #         "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_habis": waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S")
    #     }
    #     db_notifikasiIn.put(inputNotifikasiHarian)
    # elif (datetime.now().replace(tzinfo=tz_py2) >= inSore and datetime.now().replace(tzinfo=tz_py2) <= outSore):
    #     inputNotifikasiHarian = {
    #         "username": user.username,
    #         "key": str(int(generateKey(tm.time() * 10000))),
    #         "nama_kolam": (kolam.nama_kolam).lower(),
    #         "tipe": "Harian",
    #         "waktu" : "Sore",
    #         "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_habis": waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S")
    #     }
    #     db_notifikasiIn.put(inputNotifikasiHarian)

    inputNotifikasiHarian = {
        "username": user.username,
        "key": str(int(generateKey(tm.time() * 10000))),
        "nama_kolam": (kolam.nama_kolam).lower(),
        "tipe": "Harian",
        "waktu" : "Pagi",
        "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_habis": waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S")
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
        "nama_kolam": (kolam.nama_kolam).lower(),
        "tipe": "Panen",
        "waktu": "H-2",
        "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
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

@kolam_router.post("/inputdatarestock", summary="Waktu Restock Pakan Lele", response_model=RestockOut)
def menghitung_restock(nama_kolam: str, user: UserOut = Depends(get_current_user)):
    req_restock = db_kolam.fetch({'nama_kolam': (nama_kolam).lower(), 'username': user.username})

    if len(req_restock.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )
    
    if req_restock.items[0]['waktu_restock'] is not None:
        raise HTTPException(
            status_code=400,
            detail="Data already exist"
        )

    assign_restock = req_restock.items[0]
    stock_pakan_restock = assign_restock['stock_pakan']
    jumlah_pakan_harian_restock = assign_restock['jumlah_pakan_harian']

    waktu_reminder_restock_result = waktu_reminder_restock(stock_pakan_restock, jumlah_pakan_harian_restock)
    
    update = {
        "waktu_restock": waktu_reminder_restock_result.strftime("%m/%d/%Y, %H:%M:%S"),
        "allow_restock_ulang": True # Ini buat mempermudah front end
    }
    assign_restock['waktu_restock'] = waktu_reminder_restock_result.strftime("%m/%d/%Y, %H:%M:%S")
    db_kolam.update(update, assign_restock['key'])

    # Ini untuk notifikasi restock

    inputNotifikasiRestock = {
        "username": user.username,
        "key": str(int(generateKey(tm.time() * 10000))),
        "nama_kolam": (nama_kolam).lower(),
        "tipe": "Restock",
        "waktu" : "H-1",
        "waktu_masuk" : datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
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

@kolam_router.post("/restock_ulang", summary="Waktu Restock Ulang Pakan Lele", response_model=RestockUlangOut)
def restock_ulang(nama_kolam: str, stock_pakan: float, user: UserOut = Depends(get_current_user)):
    req_restock = db_kolam.fetch({'nama_kolam': (nama_kolam).lower(), 'username': user.username})

    if len(req_restock.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Data not exist"
        )

    req_restock_notif_harian = db_notifikasiIn.fetch({'nama_kolam': req_restock.items[0]['nama_kolam'], 'username': req_restock.items[0]['username'], 'waktu': 'Reminder', 'tipe': 'Harian'})   

    if len(req_restock_notif_harian.items) == 0:
        raise HTTPException(
            status_code=400,
            detail="Kolam masih belum membutuhkan restock ulang atau belum melakukan restock awal"
        ) 

    assign_restock = req_restock.items[0]
    jumlah_pakan_harian_restock = hitung_jumlah_pakan(assign_restock['jumlah_lele'], assign_restock['berat_lele'], 3.5, 0.5, stock_pakan)
    waktu_reminder_restock_result = waktu_reminder_restock(stock_pakan, jumlah_pakan_harian_restock)

    update = {
        "jumlah_pakan_harian": jumlah_pakan_harian_restock,
        "stock_pakan": stock_pakan,
        "waktu_restock": waktu_reminder_restock_result.strftime("%m/%d/%Y, %H:%M:%S"),
    }

    db_kolam.update(update, assign_restock['key'])

    assign_restock['jumlah_pakan_harian'] = jumlah_pakan_harian_restock
    assign_restock['stock_pakan'] = stock_pakan
    assign_restock['waktu_restock'] = waktu_reminder_restock_result.strftime("%m/%d/%Y, %H:%M:%S")

    # inT1 = time(17, 00, 1)
    # inT2 = time(8, 00, 1)
    # inT3 = time(12, 00, 1)

    # outT1 = time(8, 00, 00)
    # outT2 = time(12, 00, 00)
    # outT3 = time(17, 00, 00)

    # inPagi = datetime.combine(datetime.now().date(), inT1).replace(tzinfo=tz_py2) + relativedelta(days=-1)
    # inSiang = datetime.combine(datetime.now().date(), inT2).replace(tzinfo=tz_py2)
    # inSore = datetime.combine(datetime.now().date(), inT3).replace(tzinfo=tz_py2)
    # outPagi = datetime.combine(datetime.now().date(), outT1).replace(tzinfo=tz_py2)
    # outSiang = datetime.combine(datetime.now().date(), outT2).replace(tzinfo=tz_py2)
    # outSore = datetime.combine(datetime.now().date(), outT3).replace(tzinfo=tz_py2)

    # if (datetime.now().replace(tzinfo=tz_py2) >= inPagi and datetime.now().replace(tzinfo=tz_py2) <= outPagi):
    #     notifikasi_update_harian = {
    #         "waktu" : "Pagi",
    #         "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S")
    #     }
    #     db_notifikasiIn.update(notifikasi_update_harian, req_restock_notif_harian.items[0]['key']) # Ini buat harian
    # elif (datetime.now().replace(tzinfo=tz_py2) >= inSiang and datetime.now().replace(tzinfo=tz_py2) <= outSiang):
    #     notifikasi_update_harian = {
    #         "waktu" : "Siang",
    #         "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S")
    #     }
    #     db_notifikasiIn.update(notifikasi_update_harian, req_restock_notif_harian.items[0]['key']) # Ini buat harian
    # elif (datetime.now().replace(tzinfo=tz_py2) >= inSore and datetime.now().replace(tzinfo=tz_py2) <= outSore):
    #     notifikasi_update_harian = {
    #         "waktu" : "Sore",
    #         "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
    #         "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S")
    #     }
    #     db_notifikasiIn.update(notifikasi_update_harian, req_restock_notif_harian.items[0]['key']) # Ini buat harian

    notifikasi_update_harian = {
        "waktu" : "Pagi",
        "waktu_masuk": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_keluar": datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S")
    }
    db_notifikasiIn.update(notifikasi_update_harian, req_restock_notif_harian.items[0]['key']) # Ini buat harian

    req_restock_notif = db_notifikasiIn.fetch({'nama_kolam': req_restock.items[0]['nama_kolam'], 'username': req_restock.items[0]['username'], 'waktu': 'Reminder', 'tipe': 'Restock'})  

    notifikasi_update_restock = {
        "waktu" : "H-1",
        "waktu_masuk" : datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_keluar" : waktu_reminder_restock_result.strftime("%m/%d/%Y, %H:%M:%S"),
        "waktu_habis" : (waktu_reminder_restock_result + relativedelta(days=+2)).strftime("%m/%d/%Y, %H:%M:%S")
    }

    db_notifikasiIn.update(notifikasi_update_restock, req_restock_notif.items[0]['key']) # Ini buat restock

    return assign_restock

    
# Mendapatkan Info Kolam
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

# Delete Info Kolam
@kolam_router.delete("/delete/", summary="Menghapus Kolam")
def delete_kolam(nama_kolam: str, user: UserOut = Depends(get_current_user)):
    req_kolam = db_kolam.fetch({'nama_kolam': (nama_kolam).lower(), 'username': user.username})

    db_kolam.delete(req_kolam.items[0]['key'])

    req_notifikasi = db_notifikasiIn.fetch({'nama_kolam': (nama_kolam).lower(), 'username': user.username})

    for i in range(0, len(req_notifikasi.items)):
        db_notifikasiIn.delete(req_notifikasi.items[i]['key'])

    return {'message': 'success', 'nama_kolam': nama_kolam}

# Search Info Kolam
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

# Cron Job Deta dengan Trigger 1 menit sekali
# @app.lib.cron()
@app.get("/proses_notifikasi", summary="Proses Notifikasi di Cron Job", tags=["methods in cron job"])
def proses_notifikasi(e = None):
    inT1 = time(8, 00, 00)
    inT2 = time(12, 00, 00)
    inT3 = time(17, 00, 00)

    outT1 = time(9, 00, 00)
    outT2 = time(13, 00, 00)
    outT3 = time(18, 00, 00)

    inPagi = datetime.combine(datetime.now().date(), inT1).replace(tzinfo=tz_py2)
    inSiang = datetime.combine(datetime.now().date(), inT2).replace(tzinfo=tz_py2)
    inSore = datetime.combine(datetime.now().date(), inT3).replace(tzinfo=tz_py2)
    outPagi = datetime.combine(datetime.now().date(), outT1).replace(tzinfo=tz_py2)
    outSiang = datetime.combine(datetime.now().date(), outT2).replace(tzinfo=tz_py2)
    outSore = datetime.combine(datetime.now().date(), outT3).replace(tzinfo=tz_py2)

    notif_resHarian = db_notifikasiIn.fetch({"tipe":"Harian"})
    all_itemsHarian = notif_resHarian.items

    for i in range(0, len(all_itemsHarian)):
        # Ini untuk notifikasi harian
        if (datetime.now().replace(tzinfo=tz_py2).date() >= datetime.strptime((all_itemsHarian[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and datetime.now().replace(tzinfo=tz_py2).date() <= datetime.strptime((all_itemsHarian[i]['waktu_habis']), "%m/%d/%Y, %H:%M:%S").date()):

            haventRestock = db_notifikasiIn.fetch({"nama_kolam": all_itemsHarian[i]['nama_kolam'], "username": all_itemsHarian[i]['username'], "tipe": "Restock"})
            havePanen = db_notifikasiIn.fetch({"nama_kolam": all_itemsHarian[i]['nama_kolam'], "username": all_itemsHarian[i]['username'], "tipe": "Panen"})   

            # Check if there are any "Restock" items
            if haventRestock.items:
                # Check if the "Restock" item is in the "Done" state and the "Panen" item is not in the "Done" or "Stop" state
                if haventRestock.items[0]['waktu'] == "Done" and havePanen.items[0]['waktu'] not in ("Done", "Stop"):
                    # Generate a new "Harian" item
                    outputNotifikasiHarian = {
                        "username": all_itemsHarian[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "nama_kolam": all_itemsHarian[i]['nama_kolam'],
                        "tipe": "Harian",
                        "waktu": "Reminder",
                        "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Belum Restock Pakan!"
                    }
                    # Add the new item to the database
                    db_notifikasiOut.put(outputNotifikasiHarian)
                    # Update the current "Harian" and "Restock" items to the "Reminder" state
                    notifikasi_update = {
                        "waktu": "Reminder"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
                    db_notifikasiIn.update(notifikasi_update, haventRestock.items[0]['key'])
            # If there are no "Restock" items, check the state of the "Panen" item
            elif haventRestock.items:
                if havePanen.items[0]['waktu'] == "Stop":
                    # Update the current "Harian" item to the "Stop" state
                    notifikasi_update = {
                        "waktu": "Stop"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
                # Check if the "Panen" item is in the "Done" state
                elif havePanen.items[0]['waktu'] == "Done":
                    # Update the current "Harian" and "Panen" items to the "Stop" state
                    notifikasi_update = {
                        "waktu": "Stop"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
                    db_notifikasiIn.update(notifikasi_update, havePanen.items[0]['key'])
            else:
                if (datetime.now().replace(tzinfo=tz_py2) >= inPagi and datetime.now().replace(tzinfo=tz_py2) <= outPagi and all_itemsHarian[i]['waktu'] == "Pagi"):
                    outputNotifikasiHarian = {
                        "username": all_itemsHarian[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "nama_kolam": all_itemsHarian[i]['nama_kolam'],
                        "tipe": "Harian",
                        "waktu": "Pagi",
                        "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder untuk memberi pakan pada Pagi hari!"
                    }
                    db_notifikasiOut.put(outputNotifikasiHarian)
                    notifikasi_update = {
                        "waktu": "Siang"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
                elif (datetime.now().replace(tzinfo=tz_py2) >= inSiang and datetime.now().replace(tzinfo=tz_py2) <= outSiang and all_itemsHarian[i]['waktu'] == "Siang"):
                    outputNotifikasiHarian = {
                        "username": all_itemsHarian[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "nama_kolam": all_itemsHarian[i]['nama_kolam'],
                        "tipe": "Harian",
                        "waktu": "Siang",
                        "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder untuk memberi pakan pada Siang hari!"
                    }
                    db_notifikasiOut.put(outputNotifikasiHarian)
                    notifikasi_update = {
                        "waktu": "Sore"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])
                elif (datetime.now().replace(tzinfo=tz_py2) >= inSore and datetime.now().replace(tzinfo=tz_py2) <= outSore and all_itemsHarian[i]['waktu'] == "Sore"):
                    outputNotifikasiHarian = {
                        "username": all_itemsHarian[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "nama_kolam": all_itemsHarian[i]['nama_kolam'],
                        "tipe": "Harian",
                        "waktu": "Sore",
                        "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder untuk memberi pakan pada Sore hari!"
                    }
                    db_notifikasiOut.put(outputNotifikasiHarian)
                    notifikasi_update = {
                        "waktu": "Pagi"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsHarian[i]['key'])

    notif_resPanen = db_notifikasiIn.fetch({"tipe":"Panen"})
    all_itemsPanen = notif_resPanen.items

    # Yang di bawah lebih baik jika dilock
    for i in range(0, len(all_itemsPanen)):        
        # Ini untuk notifkasi panen
        if (datetime.now().replace(tzinfo=tz_py2).date() >= datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and datetime.now().replace(tzinfo=tz_py2).date() <= datetime.strptime((all_itemsPanen[i]['waktu_habis']), "%m/%d/%Y, %H:%M:%S").date()):
            if (datetime.now().replace(tzinfo=tz_py2).date() == datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date()) :
                if (datetime.now().replace(tzinfo=tz_py2) >= datetime.combine(datetime.now().date(), time(10, 1, 00)).replace(tzinfo=tz_py2) and datetime.now().replace(tzinfo=tz_py2) <= datetime.combine(datetime.now().date(), time(11, 2, 00)).replace(tzinfo=tz_py2) and all_itemsPanen[i]['waktu'] == "H-2"):
                    outputNotifikasiPanen = {
                        "username": all_itemsPanen[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "nama_kolam": all_itemsPanen[i]['nama_kolam'],
                        "tipe": "Panen",
                        "waktu": "H-2",
                        "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-2 Sebelum Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    notifikasi_update = {
                        "waktu": "H-1"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])
            elif (datetime.now().replace(tzinfo=tz_py2).date() == datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() + relativedelta(days=+1)):
                if (datetime.now().replace(tzinfo=tz_py2) >= datetime.combine(datetime.now().date(), time(10, 1, 00)).replace(tzinfo=tz_py2) and datetime.now().replace(tzinfo=tz_py2) <= datetime.combine(datetime.now().date(), time(11, 2, 00)).replace(tzinfo=tz_py2) and all_itemsPanen[i]['waktu'] == "H-1"):
                    outputNotifikasiPanen = {
                        "username": all_itemsPanen[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "nama_kolam": all_itemsPanen[i]['nama_kolam'],
                        "tipe": "Panen",
                        "waktu": "H-1",
                        "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Reminder H-1 Sebelum Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    notifikasi_update = {
                        "waktu": "H-Day"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])
            elif (datetime.now().replace(tzinfo=tz_py2).date() == datetime.strptime((all_itemsPanen[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() + relativedelta(days=+2)) and all_itemsPanen[i]['waktu'] == "H-Day":
                if (datetime.now().replace(tzinfo=tz_py2) >= datetime.combine(datetime.now().date(), time(10, 1, 00)).replace(tzinfo=tz_py2) and datetime.now().replace(tzinfo=tz_py2) <= datetime.combine(datetime.now().date(), time(11, 00, 00)).replace(tzinfo=tz_py2) and all_itemsPanen[i]['waktu'] == "H-Day"):
                    outputNotifikasiPanen = {
                        "username": all_itemsPanen[i]['username'],
                        "key": str(int(generateKey(tm.time() * 10000))),
                        "nama_kolam": all_itemsPanen[i]['nama_kolam'],
                        "tipe": "Panen",
                        "waktu": "H-Day",
                        "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                        "messages" : "Waktunya Panen!"
                    }
                    db_notifikasiOut.put(outputNotifikasiPanen)
                    notifikasi_update = {
                        "waktu": "Done"
                    }
                    db_notifikasiIn.update(notifikasi_update, all_itemsPanen[i]['key'])

    notif_resRestock = db_notifikasiIn.fetch({"tipe":"Restock"})
    all_itemsRestock = notif_resRestock.items

    for i in range(0, len(all_itemsRestock)):
        # Ini untuk notifikasi restock
        if (datetime.now().replace(tzinfo=tz_py2).date() >= datetime.strptime((all_itemsRestock[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date() 
        and datetime.now().replace(tzinfo=tz_py2).date() <= datetime.strptime((all_itemsRestock[i]['waktu_habis']), "%m/%d/%Y, %H:%M:%S").date()):

            havePanen = db_notifikasiIn.fetch({"nama_kolam": all_itemsHarian[i]['nama_kolam'], "username": all_itemsHarian[i]['username'], "tipe": "Panen"}) 
            
            # Check if the item exists and if it's in the "Stop" or "Done" state
            if havePanen and (havePanen.items[0]['waktu'] == "Stop" or havePanen.items[0]['waktu'] == "Done"):
                # Fetch the current item
                currentItem = all_itemsRestock[i]

                # Only update the item if it's not already in the "Stop" state
                if currentItem['waktu'] != "Stop":
                    notifikasi_update = {
                        "waktu": "Stop"
                    }
                    db_notifikasiIn.update(notifikasi_update, currentItem['key'])

                    # If the "Panen" item is in the "Done" state, update it as well
                    if havePanen.items[0]['waktu'] == "Done":
                        db_notifikasiIn.update(notifikasi_update, havePanen.items[0]['key'])
            else:
                if (datetime.now().replace(tzinfo=tz_py2).date() == datetime.strptime((all_itemsRestock[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date()):
                    if (datetime.now().replace(tzinfo=tz_py2) >= datetime.combine(datetime.now().date(), time(10, 2, 00)).replace(tzinfo=tz_py2) and datetime.now().replace(tzinfo=tz_py2) <= datetime.combine(datetime.now().date(), time(11, 3, 00)).replace(tzinfo=tz_py2) and all_itemsRestock[i]['waktu'] == "H-1"):
                        outputNotifikasiRestock = {
                            "username": all_itemsRestock[i]['username'],
                            "key": str(int(generateKey(tm.time() * 10000))),
                            "nama_kolam": all_itemsRestock[i]['nama_kolam'],
                            "tipe": "Restock",
                            "waktu": "H-1",
                            "waktu_keluar" : datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                            "messages" : "Reminder H-1 Sebelum Restock Pakan!"
                        }
                        db_notifikasiOut.put(outputNotifikasiRestock)
                        notifikasi_update = {
                            "waktu": "H-Day"
                        }
                        db_notifikasiIn.update(notifikasi_update, all_itemsRestock[i]['key'])
                elif (datetime.now().replace(tzinfo=tz_py2).date() == datetime.strptime((all_itemsRestock[i]['waktu_keluar']), "%m/%d/%Y, %H:%M:%S").date()  + relativedelta(days=+1)):
                    if (datetime.now().replace(tzinfo=tz_py2) >= datetime.combine(datetime.now().date(), time(10, 2, 00)).replace(tzinfo=tz_py2) and datetime.now().replace(tzinfo=tz_py2) <= datetime.combine(datetime.now().date(), time(11, 3, 00)).replace(tzinfo=tz_py2) and all_itemsRestock[i]['waktu'] == "H-Day"):
                        outputNotifikasiRestock = {
                            "username": all_itemsRestock[i]['username'],
                            "key": str(int(generateKey(tm.time() * 10000))),
                            "nama_kolam": all_itemsRestock[i]['nama_kolam'],
                            "tipe": "Restock",
                            "waktu": "H-Day",
                            "waktu_keluar": datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
                            "messages": "Waktunya Restock Pakan!"
                        }
                        db_notifikasiOut.put(outputNotifikasiRestock)
                        notifikasi_update = {
                            "waktu": "Done"
                        }
                        db_notifikasiIn.update(notifikasi_update, all_itemsRestock[i]['key'])

    # This is for return the value that in db, all of values, and it's just called it rn so it must be the recent one
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
        "tanggal_berita_dan_pedoman": datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
        "isi_berita_dan_pedoman": berita.isi_berita_dan_pedoman,
        "thumbnail": None
    }

    try:
        validated_new_berita = BeritaDanPedomanDB(**berita)
        db_beritadanpedoman.put(validated_new_berita.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    return berita

#admin - pedoman
@admin_router.post("/post/pedoman", response_model=BeritaDanPedomanDB)
def post_pedoman(pedoman: BeritaDanPedomanIn):

    pedoman = {
        'key': str(int(generateKey(tm.time() * 10000))),
        'tipe': "pedoman",
        'judul_berita_dan_pedoman': pedoman.judul_berita_dan_pedoman,
        'tanggal_berita_dan_pedoman': datetime.now(tz).strftime("%m/%d/%Y, %H:%M:%S"),
        'isi_berita_dan_pedoman': pedoman.isi_berita_dan_pedoman,
        'thumbnail': None
    }

    try:
        validated_new_pedoman = BeritaDanPedomanDB(**pedoman)
        db_beritadanpedoman.put(validated_new_pedoman.dict())
    except ValidationError:
        raise HTTPException(
            status_code=404,
            detail="Invalid input value"
        )

    return pedoman

@admin_router.post("/post/beritapedoman/thumbnail", response_model=BeritaDanPedomanDB)
async def post_thumbnail(beritadanpedoman_id: str, request: Request, img: UploadFile):
    req_beritapedoman = db_beritadanpedoman.fetch({'key': beritadanpedoman_id})

    if req_beritapedoman.items == []:
        raise HTTPException(
            status_code=404,
            detail="Berita not found"
        )
    
    id = generate_id()
    file_content = await img.read()
    file_name = f"{id}_{req_beritapedoman.items[0]['judul_berita_dan_pedoman']}.jpg"
    drive_thumbnail.put(file_name, file_content)

    thumbnail_update = {
        "thumbnail": f"{request.base_url}cdn/{file_name}"
    }

    req_beritapedoman.items[0]['thumbnail'] = f"{request.base_url}cdn/{file_name}"
    db_beritadanpedoman.update(thumbnail_update, req_beritapedoman.items[0]['key'])

    return req_beritapedoman.items[0]

# Menghapus berita dan pedoman berdasarkan id
@admin_router.delete("/delete/beritadanpedoman", summary="Delete Berita atau Pedoman")
def delete_beritapedoman(beritadanpedoman_id: str):
    req_pedoman = db_beritadanpedoman.fetch({"key": beritadanpedoman_id})

    if req_pedoman.items == []:
        raise HTTPException(
        status_code=404,
        detail="Berita atau Pedoman not found"
        )

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

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)

