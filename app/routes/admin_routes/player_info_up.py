
from app.db import model
from sqlalchemy.sql import select 
from app.db.db_conn import asyncSession
from typing import Annotated,AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas import PlayerStatisticsUpate
from fastapi import APIRouter,Depends,HTTPException,status
from app.routes.current_user import get_current_admin_user


router = APIRouter(tags=["Player_Score_Update"])

async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with asyncSession() as session:
        yield session

@router.put("/update/batting/info/{player_id}")
async def update_batting_info(player_id:int,update_info:PlayerStatisticsUpate,sess: Annotated[AsyncSession,Depends(asyncSession)],user=Depends(get_current_admin_user)):
    async with sess() as sess:
        info = sess.execute(
            select(model.PlayerStats).where(model.PlayerStats.player_id==player_id))
        player = info.scalar_one_or_none()
        
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Player not found")

        
    