from datetime import datetime,timezone
from app.db import model
from fastapi import FastAPI
from sqlalchemy.sql import text
from contextlib import asynccontextmanager
from app.db.db_conn import async_engine
from app.logger import setup_logger 

logger = None  

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --------------------Application startup------------------
    print("Application startup started")
    global logger
    try:
        logger = setup_logger()
        logger.info("Logger setup completed during startup.")

        async with async_engine.begin() as conn:
            print("Database connection established")
            await conn.run_sync(model.Base.metadata.create_all)
            date = datetime.now(timezone.utc).strftime("%d/%m/%Y, %H:%M:%S")
            logger.info("-----------------------------------")
            logger.info(f"Database schema created at {date}") 
            logger.info("-----------------------------------")

        print("Application startup completed")
        yield
    except Exception as e:
        if logger:
            logger.error(f"Startup error: {e}")
        else:
            print(f"Startup error: {e}")
        raise
    # --------------------Application Shutdown-----------------
    try:
        await async_engine.dispose()
        if logger:
            logger.info("Database connections closed")
        print("Database connections closed")
    except Exception as e:
        if logger:
            logger.error(f"Error while shutting down from lifespan: {e}")
        else:
            print(f"Error while shutting down from lifespan: {e}")

