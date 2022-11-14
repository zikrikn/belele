from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya OR using NEXT.js

#Routers
from .routers.admin import admin_router
from .routers.both import both_router
from .routers.user import user_router

#Auth
from .auth.auth_router import *

#Database
from db import *

app = FastAPI(
    title="LeMES",
    version="1.0",
    prefix="/api"
)

app.include_router(admin_router)
app.include_router(both_router)
app.include_router(user_router)
app.include_router(auth_router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@auth_router.post('/secret')
async def secret_data(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return 'Top Secret data only authorized users can access this info'

@auth_router.get('/notsecret')
async def not_secret_data():
    return 'Not secret data'

app.add_middleware(
    CORSMiddleware,
    #allow_origins=['http://app.lemes.my.id', 'https://app.lemes.my.id'],
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

