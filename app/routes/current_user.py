import os 
import jwt
from app.config import CONFIG
from dotenv import load_dotenv
from app.db.model import Player
from app.db.schemas import USERME
from sqlalchemy.sql import select
from typing import Annotated
from app.db.db_conn import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,APIRouter,HTTPException
from app.internal.error import UserIdNotFound, UserNotFound, ExpireToken


SECRET = CONFIG.SECRET_KEY
ALGORITHM = CONFIG.ALGORITHM


async def verify_token(token: str, sess: AsyncSession):
    try:
        payload = jwt.decode(token,SECRET, algorithms=ALGORITHM)
        print(f"Decoded payload: {payload}")
        user_id = payload.get("email")
        if user_id:
            result = await sess.execute(
                select(Player).filter(Player.email == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                return user 
            else:
                raise UserNotFound
        else:
            raise UserIdNotFound
        
    except jwt.ExpiredSignatureError:
        raise ExpireToken
    
    
#oauth2 scheme:
version = "v1"
tokenURL = f"/api/{version}/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenURL)


#get the current user: when a user authorized:
async def get_current_user(token: str = Depends(oauth2_scheme), sess: Annotated[AsyncSession, Depends(get_db)] = None):
    try: 
        user = await verify_token(token, sess)
        return user 
    except Exception as e:
        raise ExpireToken
    

#get current admin user: 
async def get_current_admin_user(token: str = Depends(oauth2_scheme), sess: Annotated[AsyncSession, Depends(get_db)] = None):
    try: 
        user = await verify_token(token, sess)
        if user.role.value == "admin":
            return user 
        else:
            raise HTTPException(status_code=403, detail="You are not an admin user.")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or you are not an admin user.")
    

#<----------------------Router End Point------------------------------->
router = APIRouter(tags=["Current User"])
@router.post("/user/me",response_model=USERME)
async def currentUser(user = Depends(get_current_user)):
    #print(user)
    user = USERME(
        email = user.email,
        id= user.id
    )
    return user 

@router.post("/user/admin/me",response_model=USERME)
async def currentUser(user = Depends(get_current_admin_user)):
    #print(user)
    user = USERME(
        email = user.email,
        id= user.id
    )
    return user 




