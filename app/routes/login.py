
import jwt 
from app.config import CONFIG
from app.db import schemas,model
from sqlalchemy.sql import select
from app.db.db_conn import asyncSession
from datetime import timedelta,datetime,timezone
from app.db.internal.passHassing import verify_password
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter,Depends,HTTPException,status


router = APIRouter(tags=['login'])

# Token generation endpoint/login endpoint
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    print(user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"id": user.id, "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ======================== Necessary function ========================
ALGORITHRM = CONFIG.ALGORITHM
SECRET = CONFIG.SECRET_KEY
TIME = CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES


#authenticate user
async def authenticate_user(username: str, password: str):
    async with asyncSession() as sess:
        result = await sess.execute(
                    select(model.Player).filter(model.Player.email == username)
                )
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    

# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(TIME))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,SECRET, algorithm=ALGORITHRM)
    return encoded_jwt


