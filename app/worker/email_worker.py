
from celery import Celery
from app.config import CONFIG
from asgiref.sync import async_to_sync 
from app.routes.send_mail import create_message,mail


email_task = Celery(
    main="email_sending_task",
    broker=CONFIG.REDIS_DB_URL,
    backend=CONFIG.REDIS_DB_URL
)


email_task.conf.update(
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
    
    
    #Queue-limit:
    task_default_queue='email_queue',
    task_queues={
        'email_queue':{
            'exchange':'email_exchange',#take-task
            'routing_key':'email',#select the queue
            'queue_arguments':{
                # max queue length: can't take more than 50 emails in queue
                # in concurrent, if more than 50 email request came then 
                # other will be discured. So insted of this, let's wait if overloaded
                #'x-max-length':50 
            }
        }
    }
)


# check the queue status:
def check_queue_status():
    try: 
        inspector = email_task.control.inspect()
        active_task = inspector.active() or {}
        scheduled_task = inspector.scheduled() or {}
        reserved_task = inspector.reserved() or {}
        
        active_task_count =  sum(len(tasks) for tasks in active_task.values())
        scheduled_task_count = sum(len(tasks) for tasks in  scheduled_task.values())
        reserved_task_count = sum(len(tasks) for tasks in reserved_task.values())
        
        total_task_count = active_task_count + scheduled_task_count + reserved_task_count
        
        if total_task_count>10:
            print("<--------Maximum concurrency reached.Additional tasks are waiting state.------>")

        return {
                'active': active_task_count,
                'scheduled': scheduled_task_count,
                'reserved': reserved_task_count,
                'total': total_task_count
            }
    except Exception as e:
        pass 
        
 
 
@email_task.task(name="sending-email",bind=True,max_retries=3,default_retry_delay=60,acks_late=True,queue='email_queue')
def send_email_task(self, recipt:list[str],sub:str,tampleate:str):
    try:
        #check the quqe status:
        queue_status = check_queue_status()
        if queue_status and queue_status["active"]>20:
            print(f"Queue full. Task for {recipt} will wait in the queue.")
        message = create_message(recip=recipt,sub=sub,body=tampleate)
        async_to_sync(mail.send_message)(message)
    except Exception as e:
        print(f"<------failed to send email----> \n {e}")

