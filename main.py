from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Untuk CORS Middleware beda tempat. Pakai Fetch & JS untuk implementasinya OR using NEXT.js
from fastapi.responses import RedirectResponse

#Unicorn
import uvicorn

#Routers
from routers.admin import admin_router
from routers.both import both_router
from routers.user import user_router

#Auth
from auth_subpackage.auth_router import *

#Database
from db import *

app = FastAPI(
    title="LeMES",
    version="1.0",
    prefix="/api"
)

'''
@app.get("/", include_in_schema=False)
async def redirect_docs():
    return RedirectResponse("/docs")
'''

app.include_router(admin_router)
app.include_router(both_router)
app.include_router(user_router)
app.include_router(auth_router)

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

