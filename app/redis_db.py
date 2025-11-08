
import redis 
from app.config import CONFIG

redis = redis.from_url(
    url=CONFIG.REDIS_DB_URL,
     decode_responses=True 
)



