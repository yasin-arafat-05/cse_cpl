
from pydantic_settings import BaseSettings,SettingsConfigDict



class Setting(BaseSettings):
    #<--Database configuration---->
    DATABASE_URL : str = ""
    DB_ROLE_NAME : str 
    DB_PASSWORD : str 
    DB_HOST : str 
    DATABASE : str 
    DB_PORT : int 
    
    
    #<---fastapi------->
    SECRET_KEY : str 
    ALGORITHM : str 
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    SCHEMES : str 
    
    
    #<----Email--------->
    MAIL_USERNAME : str 
    MAIL_PASSWORD : str 
    MAIL_FROM : str 
    MAIL_PORT : int 
    MAIL_SERVER : str 
    MAIL_FROM_NAME : str 
    MAIL_STARTTLS : bool  = False
    MAIL_SSL_TLS : bool  = True
    USE_CREDENTIALS : bool = True
    VALIDATE_CERTS : bool = True
    model_config = SettingsConfigDict(env_file="app/.env",extra='ignore')


CONFIG = Setting()

CONFIG.DATABASE_URL = (
    f"postgresql+asyncpg://{CONFIG.DB_ROLE_NAME}:{CONFIG.DB_PASSWORD}"
    f"@{CONFIG.DB_HOST}:{CONFIG.DB_PORT}/{CONFIG.DATABASE}"
)


