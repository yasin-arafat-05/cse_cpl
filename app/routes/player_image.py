""" 
This will effect our cpu a lot: To solve this. 
- 
- pip install rembg[server]
- rembg serve --host 0.0.0.0 --port 8000
-
"""
import io
import os 
import jwt 
import json
import secrets 
from PIL import Image
from app.db import model
from typing import Annotated
from app.redis_db import redis
from sqlalchemy.sql import select
from app.db.db_conn import get_db
from fastapi import HTTPException,status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket,WebSocketDisconnect
from fastapi import APIRouter,File,UploadFile,Depends
from app.worker.image_upload_worker import player_image_uplod
from app.routes.current_user import get_current_user,get_current_admin_user

router = APIRouter(tags=['Player-Image-Upload'])

#---------------------------------------Profile Picture Uplod---------------------------------------
'''
Mount is going to tell the fastapi that in this directory will save static files likes images.
'''
router.mount("/photo", StaticFiles(directory="app/photo"), name="photo")


""" 
rembg use deep learning model.
It's a very heavy and cpu bound task.
Use lighiter model like, u2netp.
"""
@router.post("/upload/player/profile")
async def create_upload_file(sess: Annotated[AsyncSession, Depends(get_db)],file: UploadFile = File(...),user = Depends(get_current_user)):
    try:
        filename = file.filename
        ext = filename.split('.')[-1].lower()
        if ext not in ['png', 'jpg', 'jpeg']:
            return {"status": "File extension should be .png, .jpg or .jpeg"}
        
        token_name = secrets.token_hex(10) + '.png'
        output_path = os.path.join("app","photo","player",f"{token_name}")
        
        # without reading the file we can't send the file:
        await file.seek(0)
        file_bytes = await file.read()
        
        #call the celery task here:
        ack = ack = player_image_uplod.delay(
        file_bytes = file_bytes,
        output_path=output_path,
        category=user.category.value,
        email=user.email,
        token_name=token_name)
        return {"status": "task queued", "task_id": ack.id}
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



# ======================================================================
# =====  Update Background Image ===== 
#update background image:
# must be file_name should be in ["all_rounder","batsman","bolwer","wk_batsman"]
@router.put("/background/image/update")
async def update_upload_background_image(file_name:str,sess: Annotated[AsyncSession, Depends(get_db)],file : UploadFile = File(...),user = Depends(get_current_user)):
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


#<-------------websocket for notify uploding image brother:----------------->
@router.websocket("/ws/photo/upload/notification")
async def photo_upload_notification(websocket : WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return 
    user =  jwt.decode(token)
    email = user["email"]
    
    pubsub = redis.pubsub()
    pubsub.subscribe(f"notify:{email}")
    
    try:
        for messages in pubsub.listen():
            if messages["type"] == "message":
                data = json.loads(messages["data"])
                await websocket.send_json(data)
                break 
    except WebSocketDisconnect:
        pubsub.close()
    finally:
        await websocket.close()
        


