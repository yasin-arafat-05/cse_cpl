


from app.db import model
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from typing import Annotated
from app.db.db_conn import get_db
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(tags=['Admin-Get-All-Player'])



# 1. Get all players in our platfrom:
@router.get("all/players")
async def get_available_players_for_auction(sess: Annotated[AsyncSession, Depends(get_db)]):
    try:
        result = await sess.execute(
            select(model.Player)
        )
        players = result.scalars().all()
        total_players = len(players)
        return {
                "total_players": total_players,
                "all_player_list": [
                {
                "id": p.id,
                "name": p.name,
                "email": p.email,
                "category": p.category.value,
                "photo_url": p.photo_url
            }
            for p in players]
        }
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Failed to fetch players")
        
        

