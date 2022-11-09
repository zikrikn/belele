from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya
from schemas.admin import *
from schemas.pemberipakan import *
from db import *
#Auth user
from auth import Auth
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Fokus untuk membuat REST API-nya buat backend

app = FastAPI(
    title="LeMES",
    version="1.0",
    prefix="/api"
)

#Auto handler
security = HTTPBearer()
auth_handler = Auth()

@app.get("/hi")
async def main():
    return {"message": "Hello World"}

@app.get("/")
def read_root():
    return {"Hello": "World"}

#Making real API

@app.post("/admin")
async def create_item(admin: Admin):
    admins =  db_admin.put(admin.dict()) #Ini put/create ke database
    return admins

#Membuat auth untuk login

#Sign up
@app.post('/signup')
def signup(user_details: PemberiPakan):
    if db_pemberipakan.get(user_details.key) != None:
        return 'Account already exists'
    try:
        hashed_password = auth_handler.encode_password(user_details.PasswordPP)
        user = {'key': user_details.key, 'password': hashed_password}
        return db_pemberipakan.put(user)
    except:
        error_msg = 'Failed to signup user'
        return error_msg

@app.post('/login')
def login(user_details: PemberiPakan):
    user = db_pemberipakan.get(user_details.key)
    if (user is None):
        return HTTPException(status_code=401, detail='Invalid username')
    if (not auth_handler.verify_password(user_details.PasswordPP, user['password'])):
        return HTTPException(status_code=401, detail='Invalid password')
    
    access_token = auth_handler.encode_token(user['key'])
    refresh_token = auth_handler.encode_refresh_token(user['key'])
    return {'access_token': access_token, 'refresh_token': refresh_token}

@app.get('/refresh_token')
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token}

@app.post('/secret')
def secret_data(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return 'Top Secret data only authorized users can access this info'

@app.get('/notsecret')
def not_secret_data():
    return 'Not secret data'

app.add_middleware(
    CORSMiddleware,
    #allow_origins=['http://app.lemes.my.id', 'https://app.lemes.my.id'],
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

