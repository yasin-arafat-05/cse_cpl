from app.config import CONFIG
import logging
from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker


connection_string = CONFIG.DATABASE_URL

app_logger = logging.getLogger("cpl_logger.py")

async_engine = create_async_engine(
    url=connection_string,
    # Connection Pool Settings
    pool_size=20,      
    max_overflow=10,   
    pool_timeout=30,  
    pool_recycle=1800, 
    pool_pre_ping=True,
    echo=False #Set to False in production
)


asyncSession = async_sessionmaker(
    bind= async_engine,
    class_= AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


Base = declarative_base()


# database utility: 
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with asyncSession() as session:
        app_logger.debug("DB session opened")
        try:
            yield session
        except Exception as e:
            app_logger.exception(f"DB session error, rolling back: {e}")
            await session.rollback() 
            raise
        finally:
            app_logger.debug("DB session closed")


