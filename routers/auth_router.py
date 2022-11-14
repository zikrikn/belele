from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth_class import Auth
from schemas.pemberipakan import *
from db import *

auth_router = APIRouter(tags=["Auth"])

#Auto handler
security = HTTPBearer()
auth_handler = Auth()

#Membuat auth untuk login dan signup
#!!!Tambahannya signup admin dan delete akun!!!

@auth_router.post('/signup')
async def signup(user_details: PemberiPakan):
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
async def login(user_details: PemberiPakan):
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

'''
@auth_router.post('/secret')
def secret_data(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return 'Top Secret data only authorized users can access this info'

@auth_router.get('/notsecret')
def not_secret_data():
    return 'Not secret data'
'''