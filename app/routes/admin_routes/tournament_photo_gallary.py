import io
import os 
import secrets 
from PIL import Image
from app.db import model
from app.db import schemas
from typing import Annotated
from app.db.db_conn import get_db
from sqlalchemy.sql import select
from fastapi import BackgroundTasks
from rembg import new_session,remove
from fastapi import HTTPException,status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes.current_user import get_current_user
from fastapi import APIRouter,File,UploadFile,Depends


router = APIRouter(tags=['Tounament-Image-Upload'])


#---------------------------------------Profile Picture Uplod---------------------------------------
'''
Mount is going to tell the fastapi that in this directory will save static files likes images.
'''
router.mount("/photo", StaticFiles(directory="app/photo"), name="photo")
@router.post("/upload/tounament/image")
async def tournament_image_upload(tounament_id:int, sess: Annotated[AsyncSession, Depends(get_db)], file: UploadFile = File(...), bgtask : BackgroundTasks = None, user = Depends(get_current_user)):
  try:
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    if ext not in ['png', 'jpg', 'jpeg']:
        return {"status": "File extension should be .png, .jpg or .jpeg"}
    token_name = secrets.token_hex(10) + '.png'
    
    tournament_result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == tounament_id)
        )
    tournament = tournament_result.scalar_one_or_none()
    if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found-> upload tounament image")
    
    image_dir = os.path.join("app","photo","tounaments",f"{token_name}")

    total_image= await get_tounament_image_files(tounament_id)
    total_image_len = len(total_image)
        
    if total_image_len>10: 
             raise HTTPException(status_code=404, detail="Can't upload more than ten image")
        
    # user input image:
    file_content = await file.read()
    input_image = Image.open(io.BytesIO(file_content)).convert("RGBA")
    input_image.save(image_dir)
        
    image_info = model.TounamnetImage(
            tournament_id = tounament_id,
            photo_url = image_dir
    )
        
    sess.add(image_info)
    await sess.commit()
    await sess.refresh(image_info)
    await file.close()
    return {"status": "success", "filename": token_name}
  except Exception as e:
      print(e)
      raise HTTPException(status_code=404, detail="Can't upload tounament image brother")


#--------------------------get the image-------------------------
from fastapi.responses import FileResponse

# tounament all image files brother:
@router.get("/tounament/image/files")
async def get_tounament_image_files(tounament_id:int,sess: Annotated[AsyncSession, Depends(get_db)]):
    try:
        tournament_result = await sess.execute(
            select(model.TounamnetImage).where(model.TounamnetImage.tournament_id == tounament_id))
        image_list = tournament_result.scalars().all()
        return [
            {"photo_url": img.photo_url} for img in image_list
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch tournament images")

    
# tounament image:
@router.get("/tounament/image/{filename}")
async def get_touament_image(filename: str):
    try:
        final_path = os.path.join("app","photo","tounaments",f"{filename}")
        return FileResponse(final_path)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch tournament image")


