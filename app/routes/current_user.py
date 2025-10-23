import os 
import jwt
from app.config import CONFIG
from dotenv import load_dotenv
from app.db.model import Player
from app.db.schemas import USERME
from sqlalchemy.sql import select
from fastapi import Depends,APIRouter
from app.db.db_conn import asyncSession
from fastapi.security import OAuth2PasswordBearer
from app.internal.error import UserIdNotFound, UserNotFound, ExpireToken


SECRET = CONFIG.SECRET_KEY
ALGORITHM = CONFIG.ALGORITHM


async def verify_token(token: str):
    try:
        payload = jwt.decode(token,SECRET, algorithms=ALGORITHM)
        print(f"Decoded payload: {payload}")
        user_id = payload.get("email")
        if user_id:
            async with asyncSession() as sess:
                result = await sess.execute(
                    select(Player).filter(Player.email == user_id)
                )
                user = result.scalar_one_or_none()
            if user:
                
                return { "id": user.id,
                        "email": user.email}
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
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try: 
        user = await verify_token(token)
        return user 
    except Exception as e:
        raise ExpireToken
    
#<----------------------Router End Point------------------------------->
router = APIRouter(tags=["Current User"])
@router.post("/user/me",response_model=USERME)
async def currentUser(user = Depends(get_current_user)):
    #print(user)
    user = USERME(
        email = user["email"],
        id= user["id"]
    )
    return user 




