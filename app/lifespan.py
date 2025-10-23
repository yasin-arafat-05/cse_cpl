
from app.db import model
from fastapi import FastAPI
from sqlalchemy.sql import text 
from contextlib import asynccontextmanager
from app.db.db_conn import async_engine


@asynccontextmanager
async def lifespan(app:FastAPI):
    #--------------------Applicatoin startup------------------
    print("Application startup started")
    global complied_graph
    try:
        # a.Create Database Schema:
        async with async_engine.begin() as conn:
            print("Database connection established")
            await conn.run_sync(fn=model.Base.metadata.create_all)
            print("Application startup completed")
        
            # hand control to FastAPI while pool/conn contexts remain open
            yield 
    except Exception as e:
        print(f"Startup error: {e}")
        raise
    
    #--------------------Applicatoin Shutdown-----------------
    try:
        await async_engine.dispose()
        print("Database connections closed")
    except Exception as e:
        print(f"error while shuting down from lifespan: {e}")

