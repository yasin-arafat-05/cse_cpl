
import io
import secrets 
from PIL import Image
from rembg import remove
from app.db import model
from app.db import schemas
from sqlalchemy.sql import select
from app.db.db_conn import asyncSession
from fastapi import HTTPException,status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes.current_user import get_current_user
from fastapi import APIRouter,File,UploadFile,Depends

router = APIRouter(tags=['Player-Image-Upload'])


#---------------------------------------Profile Picture Uplod---------------------------------------
'''
Mount is going to tell the fastapi that in this directory will save static files likes images.
'''
router.mount("/photo", StaticFiles(directory="app/photo"), name="photo")


@router.post("/upload/player/profile")
async def create_upload_file(file: UploadFile = File(...),user = Depends(get_current_user)):
    PATH = "app/photo/player"
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    if ext not in ['png', 'jpg', 'jpeg']:
        return {"status": "File extension should be .png, .jpg or .jpeg"}
    token_name = secrets.token_hex(10) + '.png'
    output_path = f"{PATH}/{token_name}"

    # user input image:
    file_content = await file.read()
    input_image = Image.open(io.BytesIO(file_content)).convert("RGBA")

    # 1: Remove Background
    no_bg = remove(input_image)

    # 2: Load YOUR custom background image
    bg_path = "app/photo/backgrounds/Background.jpg"
    background = Image.open(bg_path).convert("RGBA").resize(no_bg.size)

    # 3: Merge custom image with our background
    position = (150,150)
    background.paste(no_bg, position, no_bg)


    #4.: Resize and save
    final_img = background.resize((1000, 1024))
    final_img.save(output_path, format="PNG")

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



#--------------------------get the image-------------------------
from fastapi.responses import FileResponse
@router.get("/Player/Profile/{filename}")
async def get_uploaded_image(filename: str):
    image_path = f"app/photo/player/{filename}"
    return FileResponse(image_path)


