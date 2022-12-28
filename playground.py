import pytz
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta

# Menentukan timezone Indonesia Barat
tz = pytz.timezone('Asia/Jakarta')

# Mengonversi waktu sekarang menjadi waktu di Indonesia Barat
local_time = datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S")
print(local_time)

print((datetime.now(tz).date() + relativedelta(days=+1)).strftime("%m/%d/%Y, %H:%M:%S"))

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

def waktu_panen(jumlah_pakan_harian, lama_panen, waktu_panen_input):
    # Hitung jumlah hari yang diperlukan untuk panen
    jumlah_hari_panen = lama_panen / jumlah_pakan_harian
    # Hitung waktu reminder panen dengan menambahkan jumlah hari yang diperlukan untuk panen pada waktu panen
    waktu_panen = waktu_panen_input + timedelta(days=jumlah_hari_panen)
    # Kembalikan waktu reminder panen dalam format YYYY-MM-DD HH:MM:SS
    return waktu_panen

waktu_panen_result = waktu_panen(hitung_jumlah_pakan(1000, 50, 3.5, 0.5, 2000), 60, (datetime.now(tz).date() + relativedelta(months=+2)))

print(waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S"))
print(type(waktu_panen_result.strftime("%m/%d/%Y, %H:%M:%S")))
print((waktu_panen_result + relativedelta(months=+2, days=+6)).strftime("%m/%d/%Y, %H:%M:%S"))

print(datetime.now(tz).date().strftime("%m/%d/%Y, %H:%M:%S"))

inT1 = time(8, 00, 00)
inT2 = time(12, 00, 00)
inT3 = time(17, 00, 00)

outT1 = time(9, 00, 00)
outT2 = time(13, 00, 00)
outT3 = time(18, 00, 00)

datetime.now()
datetime.now(tz).date()

inPagi = datetime.combine(datetime.now(tz).date(), inT1).astimezone(tz)
inSiang = datetime.combine(datetime.now(tz).date(), inT2)
inSore = datetime.combine(datetime.now(tz).date(), inT3)
outPagi = datetime.combine(datetime.now(tz).date(), outT1)
outSiang = datetime.combine(datetime.now(tz).date(), outT2)
outSore = datetime.combine(datetime.now(tz).date(), outT3)

print(inPagi)
print(datetime.now(tz))
print(datetime.now())

if inPagi <= datetime.now(tz):
    print("inPagi")

if datetime.now(tz).date() > datetime.strptime(("12/10/2022, 00:00:00"), "%m/%d/%Y, %H:%M:%S").date():
    print("Berjalan")

print(datetime.strptime(("12/28/2022, 00:00:00"), "%m/%d/%Y, %H:%M:%S").date())

print(datetime.now(tz).date())