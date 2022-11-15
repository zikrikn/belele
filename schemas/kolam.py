from pydantic import BaseModel

'''
Inputnya mau apa di In
Outputnya mau apa di Out
Data DB yang mau di-store di masukan ke KolamDB

Penggunaan .update
user = req_user.items[0]
user['is_active'] = True
db_user.update(user, user['key'])

Terus jangan lupa pakai handling error
itu juga fungsi dari fetch di sini

Untuk sample bisa lihat asdos sebagai referensi, especially about the auth
'''

class KolamDB(BaseModel):
    key: str #Kolam.idr
    JumlahLele: int
    UmurLele: int
    TanggalAwalTebarBibit: str
    TakaranPangan: int

class Restock(BaseModel): #This in
    key: str #Kolam.id
    JumlahPakan: int
    RestockPangan: int

class RestockOut(BaseModel): #This in
    key: str #Kolam.id
    JumlahPakan: int
    RestockPangan: int
