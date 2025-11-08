
import io 
import os 
import json
import asyncio
from PIL import Image
from app.db import model
from celery import Celery
from app.config import CONFIG
from app.redis_db import redis
from sqlalchemy.sql import select
from rembg import new_session,remove
from asgiref.sync import async_to_sync
from app.db.db_conn import asyncSession
from fastapi import HTTPException,status


image_uplaod_task = Celery(
    main="image_upload_task",
    backend=CONFIG.REDIS_DB_URL,
    broker=CONFIG.REDIS_DB_URL   
)


#update celery:
image_uplaod_task.conf.update(
    task_serializer='json',        
    accept_content=['json'],       
    result_serializer='json',     
    timezone='UTC',              
    enable_utc=True,  
    
    #concurrency-setting:
    worker_concurrency = 10,
    
    #Queue-setting:
    task_default_rate_limit="10/m",  # Rate limiting,per minitue 10 work
    task_acks_late=True,#acknowledgement later.
    task_reject_on_worker_lost=True, 
    
    #Retry settings:
    task_default_retry_delay=60,  # 1 minute delay before retry
    task_max_retries=3,
    
    #Performance settings:
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,#restart after doing 100 task
    task_time_limit=300,#task limit: 5min
    task_track_started=True,
    #if failed brocker connection after restart it will re-try
    broker_connection_retry_on_startup=True,
    
    #Result settings:
    result_expires=300,
    result_backend_always_retry=True,
    
    # Queue-limits:
    task_default_queue='upload_image',
    task_queues={
        'upload_image':{
            'exchange':'email_exchange',
            'routing_key':'email',
            'queue_arguments':{
            }
        }
    }
)



def check_queue_status():
    try:
        inspector = image_uplaod_task.control.inspect()
        active_task = inspector.active() or {}
        scheduled_task = inspector.scheduled() or {}
        reserved_task = inspector.reserved() or {}
        
        active_task_count =  sum(len(tasks) for tasks in active_task.values())
        scheduled_task_count = sum(len(tasks) for tasks in  scheduled_task.values())
        reserved_task_count = sum(len(tasks) for tasks in reserved_task.values())
        
        total_task_count = active_task_count + scheduled_task_count + reserved_task_count
        
        if total_task_count>1:
            print("<--------Maximum concurrency reached.Additional tasks are waiting state.------>")

        return {
                'active': active_task_count,
                'scheduled': scheduled_task_count,
                'reserved': reserved_task_count,
                'total': total_task_count
            }
        pass 
    except Exception as e:
        print("Excption whiel processing the image upload in queue")
        pass 



# ======= image upload logis ======
async def image_upload_queue(file_bytes,output_path,category,email,token_name):
    try: 
        async with asyncSession() as sess:
            #upload image:
            input_image = Image.open(io.BytesIO(file_bytes)).convert("RGBA")
            
            # 1: Remove background using lightweight model
            session = new_session(model_name="u2netp")
            no_bg = remove(data=input_image, session=session)
            
            # Resize the no_bg image to fit exactly the target area (500x680)
            target_size = (1563, 2125) 
            no_bg = no_bg.resize(target_size, Image.Resampling.LANCZOS) 
            
            # 2:  background (3375,3375,3)
            bg_path = os.path.join("app", "photo", "backgrounds", f"{category}.png")
            background = Image.open(bg_path).convert("RGBA")
            
            # 3: Paste the no-bg image on background 
            position = (938, 1250)
            background.paste(no_bg, position, no_bg)
            
            # 4: Resize final image and save
            final_img = background.resize((1000, 1024))
            final_img.save(output_path, format="PNG")
                    
            result = await sess.execute(select(model.Player).where(model.Player.email == email))
            curr_user = result.scalar_one_or_none()
            if not curr_user:
                redis.publish(channel=f"nofiy:{email}", message=json.dumps({
                        "status": "image is not uploaded successfully image",
                        "message": "Your image has been processed"}))
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not Authenticated User")
                    
            curr_user.photo_url = output_path
            await sess.commit()
            #await file.close()
            
            #publish a message in our redis:
            redis.publish(
                channel=f"nofiy:{email}",
                message=json.dumps({
                    "status": "successfully uploaded image",
                    "message": "Your image has been processed"
                })
            )
        return {"status": "success", "filename": token_name}
    except Exception as e:
        await sess.rollback()
        print("Image uploading Queue is faling")
        
        

# bind=true, that's means we need to pass self
@image_uplaod_task.task(name="uploading-player-image",max_retries=3,default_retry_delay=60,acks_late=True,queue='upload_image')
def player_image_uplod(file_bytes,output_path,category,email,token_name):
    try: 
        #check the queue status:
        status = check_queue_status()
        if status and status["active"]>1:
            print(f"Queue full. Task for uploading image for the user {email} will wait in the queue.")
        asyncio.run(image_upload_queue(file_bytes,output_path,category,email,token_name))
    except Exception as e:
        print("getting error while executing the task queue")






