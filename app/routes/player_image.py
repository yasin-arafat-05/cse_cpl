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
from app.db.db_conn import asyncSession
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

def background_processing(file_content, output_path):
    input_image = Image.open(io.BytesIO(file_content)).convert("RGBA")

    # 1: Remove background using lightweight model
    session = new_session(model_name="u2netp")
    no_bg = remove(data=input_image, session=session)

    # 2: Load and resize custom background
    bg_path = "app/photo/backgrounds/Background.jpg"
    background = Image.open(bg_path).convert("RGBA").resize(no_bg.size)

    # 3: Paste the no-bg image on background
    position = (250, 250)
    background.paste(no_bg, position, no_bg)

    # 4: Save final image
    final_img = background.resize((1000, 1024))
    final_img.save(output_path, format="PNG")


""" 
rembg use deep learning model.
It's a very heavy and cpu bound task.
Use lighiter model like, u2netp.
"""
@router.post("/upload/player/profile")
async def create_upload_file(file: UploadFile = File(...),bgtask : BackgroundTasks = None,user = Depends(get_current_user)):
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    if ext not in ['png', 'jpg', 'jpeg']:
        return {"status": "File extension should be .png, .jpg or .jpeg"}
    token_name = secrets.token_hex(10) + '.png'
    output_path = f"app/photo/player/{token_name}"

    # user input image:
    file_content = await file.read()
    bgtask.add_task(background_processing,file_content,output_path)

    #5. Update Database
    async with asyncSession() as sess:
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


# ============== get the image ==========================
from fastapi.responses import FileResponse
@router.get("/player/profile/{filename}")
async def get_uploaded_image(filename: str):
    image_path = os.path.join("app","photo","player",f"{filename}")
    return FileResponse(image_path)


# =====  Update Background Image ===== 
#update background image:
@router.put("/background/image/update")
async def update_upload_background_image(file_name:str,file : UploadFile = File(...),bgtask : BackgroundTasks = None,user = Depends(get_current_user)):
    
    if file_name not in ["all_rounder","batsman","bolwer","wk_batsman"]:
        return {"status": "Incorrect Image File Name"}
    
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    if ext not in ['png', 'jpg', 'jpeg']:
        return {"status": "File extension should be .png, .jpg or .jpeg"}
    token_name = file_name + '.png'
    
    output_path = os.path.join("app","photo","backgrounds",token_name)

    # user input image:
    file_content = await file.read()
    input_image = Image.open(io.BytesIO(file_content)).convert("RGBA")
    
    async with asyncSession() as sess:
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



# background image:
@router.get("/background/image/{filename}")
async def get_background_image(filename: str,user = Depends(get_current_admin_user)):
    image_path = os.path.join("app","photo","backgrounds",f"{filename}")
    return FileResponse(image_path)


