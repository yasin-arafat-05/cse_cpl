
from typing import Annotated
from app.db import model,schemas
from app.db.db_conn import get_db
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes.send_mail import send_mail_endpoint
from app.internal.passHassing import get_password_hash
from app.internal.html_template import pstu_cse_reset_password
from fastapi import APIRouter,HTTPException,Depends,status,BackgroundTasks


router = APIRouter(tags=["Password ForgotReset"])


@router.post('/password/reset')
async def password_reset(email:schemas.PasswordReset,bg: BackgroundTasks, sess:Annotated[AsyncSession,Depends(get_db)]):
    try : 
        player_info =  await sess.execute(
            select(model.Player).where(model.Player.email == email.emails)
        )
        player_information = player_info.scalar_one_or_none()
        
        if email.new_password != email.retype_passowrd:
            return {"status":"password don't match"}
        
        player_information.password =  get_password_hash(email.new_password)
        await sess.commit()
        return {"status":"password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, 
                            detail="Something is wrong while reseting password.")
    
    
@router.post('/forgoten/password')
async def  forgoten_password(email:schemas.ForgottonPassword,background_task: BackgroundTasks,sess:Annotated[AsyncSession,Depends(get_db)]):
    try:
        player_info =  await sess.execute(
            select(model.Player).where(model.Player.email == email.email))
        player_information = player_info.scalar_one_or_none()
        
        if not player_information:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="user not found")
            
        recip = [email.email]
        sub = "Reset Password Link"
        reset_link = "https://pstu.ac.bd/faculty/faculty-of-computer-science-and-engineering"
        html = pstu_cse_reset_password(username=player_information.name,reset_link=reset_link)
        background_task.add_task(send_mail_endpoint,recip,sub,html)
        return {"status": "check your email darling."}
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, 
                            detail="Something is wrong while send the password reset email")

