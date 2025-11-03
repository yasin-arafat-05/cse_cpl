""" 
This will effect our cpu a lot: To solve this. 
- 
- pip install rembg[server]
- rembg serve --host 0.0.0.0 --port 8000
-
"""

import io
import os 
import secrets 
from PIL import Image
from app.db import model
from sqlalchemy.sql import select
from fastapi import BackgroundTasks
from rembg import new_session,remove
from typing import Annotated
from app.db.db_conn import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter,File,UploadFile,Depends
from app.routes.current_user import get_current_user,get_current_admin_user

router = APIRouter(tags=['Player-Image-Upload'])

#---------------------------------------Profile Picture Uplod---------------------------------------
'''
Mount is going to tell the fastapi that in this directory will save static files likes images.
'''
router.mount("/photo", StaticFiles(directory="app/photo"), name="photo")

def background_processing(file_content, output_path, category):
    input_image = Image.open(io.BytesIO(file_content)).convert("RGBA")
    
    # 1: Remove background using lightweight model
    session = new_session(model_name="u2netp")
    no_bg = remove(data=input_image, session=session)
    
    # Resize the no_bg image to fit exactly the target area (500x680)
    target_size = (500, 680) 
    no_bg = no_bg.resize(target_size, Image.Resampling.LANCZOS) 
    
    # 2:  background ( 1080x1080)
    bg_path = os.path.join("app", "photo", "backgrounds", f"{category}.png")
    background = Image.open(bg_path).convert("RGBA")
    
    # 3: Paste the no-bg image on background 
    position = (300, 400) 
    background.paste(no_bg, position, no_bg)
    
    # 4: Resize final image and save
    final_img = background.resize((1000, 1024))
    final_img.save(output_path, format="PNG")


""" 
rembg use deep learning model.
It's a very heavy and cpu bound task.
Use lighiter model like, u2netp.
"""
@router.post("/upload/player/profile")
async def create_upload_file(sess: Annotated[AsyncSession, Depends(get_db)],file: UploadFile = File(...),bgtask : BackgroundTasks = None,user = Depends(get_current_user)):
    try:
        filename = file.filename
        ext = filename.split('.')[-1].lower()
        if ext not in ['png', 'jpg', 'jpeg']:
            return {"status": "File extension should be .png, .jpg or .jpeg"}
        
        token_name = secrets.token_hex(10) + '.png'
        output_path = os.path.join("app","photo","player",f"{token_name}")
        file_content = await file.read()
        if bgtask is not None:
            bgtask.add_task(background_processing,file_content,output_path,user.category.value)
        else:
            background_processing(file_content, output_path)
        result = await sess.execute(select(model.Player).where(model.Player.email == user.email))
        curr_user = result.scalar_one_or_none()
        if not curr_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authenticated User"
            )
        curr_user.photo_url = output_path
        await sess.commit()
        await file.close()
        return {"status": "success", "filename": token_name}
    except HTTPException:
        raise
    except Exception:
        await sess.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload player image")


# ============== get the image ==========================
from fastapi.responses import FileResponse
@router.get("/player/profile/{filename}")
async def get_uploaded_image(filename: str):
    image_path = os.path.join("app","photo","player",f"{filename}")
    return FileResponse(image_path)


# =======================================================================
# background processing:



# =====  Update Background Image ===== 
#update background image:
# must be file_name should be in ["all_rounder","batsman","bolwer","wk_batsman"]
@router.put("/background/image/update")
async def update_upload_background_image(file_name:str,sess: Annotated[AsyncSession, Depends(get_db)],file : UploadFile = File(...),bgtask : BackgroundTasks = None,user = Depends(get_current_user)):
    try:
        if file_name not in ["all_rounder","batsman","bowler","wk_batsman"]:
            return {"status": "Incorrect Image File Name"}
        
        filename = file.filename
        ext = filename.split('.')[-1].lower()
        if ext not in ['png', 'jpg', 'jpeg']:
            return {"status": "File extension should be .png, .jpg or .jpeg"}
        token_name = file_name + '.png'
        output_path = os.path.join("app","photo","backgrounds",token_name)
        file_content = await file.read()
        input_image = Image.open(io.BytesIO(file_content)).convert("RGBA")
        rest = await sess.execute(
            select(model.BackgroundImage).where(model.BackgroundImage.file_name==file_name)
        )
        
        img_file_name = rest.scalar_one_or_none()
        if img_file_name:
            img_file_name.photo_url = output_path
            await sess.commit()
            input_image.save(output_path)
            await file.close()
            return {"status":"successful","details":"Background image update successfully"}
        write_img = model.BackgroundImage(
                file_name=file_name,
                photo_url= output_path
            )
        sess.add(write_img)
        await sess.commit()
        await sess.refresh(write_img)
        input_image.save(output_path)
        await file.close()
        return {"status":"successful","details":"Background image upload successfully"}
    except HTTPException:
        raise
    except Exception:
        await sess.rollback()
        raise HTTPException(status_code=500, detail="Failed to update background image")



# background image:
@router.get("/background/image/{filename}")
async def get_background_image(filename: str,user = Depends(get_current_admin_user)):
    try:
        image_path = os.path.join("app","photo","backgrounds",f"{filename}")
        return FileResponse(image_path)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch background image")


