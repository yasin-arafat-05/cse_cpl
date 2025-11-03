from app.db.model import Player
from sqlalchemy.sql import select
from app.db.schemas import CreateUser
from app.db.db_conn import asyncSession
from fastapi.background import BackgroundTasks
from app.internal.error import MailExistError
from fastapi import status,APIRouter,HTTPException
from app.routes.send_mail import send_mail_endpoint
from app.internal.passHassing import get_password_hash
from app.internal.html_template import pstu_cse_event_account_created

router = APIRouter(tags=['Sign-up'])

#_________________________________ REGISTRATION ENDPOINT _________________________________
@router.post('/registration', status_code=status.HTTP_201_CREATED)
async def user_registration(user: CreateUser,background_task:BackgroundTasks):
    # exclude_unset=True if user don't give any value of any filed then create new user 
    # By the default given when we create schema in database in tables.py files.
    user_data = user.model_dump(exclude_unset=True)
    user_data["password"] = get_password_hash(user_data["password"])
    async with asyncSession() as sess:
        result = await sess.execute(
                    select(Player).filter(Player.email == user_data["email"])
                )
        fnd = result.scalar_one_or_none()
        if fnd:
            raise MailExistError()
        
        try:
            new_user = Player(**user_data)
            sess.add(new_user)
            await sess.commit()
            await sess.refresh(new_user)
            
            #send email:
            recip = [user_data["email"]]
            sub = "Welcome To Our CPL Websites"
            html = pstu_cse_event_account_created(user_data["name"])
            background_task.add_task(send_mail_endpoint,recip,sub,html)
        except ValueError as e:
            await sess.rollback()
            er = f"Error occur due to: {str(e)}"
            raise HTTPException(status_code=400, detail="Your Category Or Gmail is Not Correct")
        except Exception as e:
            await sess.rollback()
            er = f"Error occur due to: {str(e)}"
            raise HTTPException(status_code=400, detail="can't make an account something went wrong")
    return {"status":200,"detail":"User Created Successfully. Please Login And Enjoy the day."}

