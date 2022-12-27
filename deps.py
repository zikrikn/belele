from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from uuid import UUID

from schemas.token import TokenPayLoad
from jose import jwt
from pydantic import ValidationError
from schemas.user import UserOut
from settings import JWT_SECRET_KEY, ALGORITHM

from db import db_user

reusable_oauth = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)

async def get_current_user(token: str = Depends(reusable_oauth)) -> UserOut:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        token_data = TokenPayLoad(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Couldn't validate credential",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    fetch_user = db_user.fetch({'key': str(token_data.sub)})
    try:
        user: Union[dict[str, Any], None] = fetch_user.items[0]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserOut(**user)
