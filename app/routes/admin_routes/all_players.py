


from app.db import model
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from app.db.db_conn import asyncSession



router = APIRouter(tags=['Admin-Get-All-Player'])



# 1. Get all players in our platfrom:
@router.get("all/players")
async def get_available_players_for_auction():
    async with asyncSession() as sess:
        result = await sess.execute(
            select(model.Player)
        )
        
        players = result.scalars().all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "email": p.email,
                "category": p.category.value,
                "photo_url": p.photo_url
            }
            for p in players
        ]
        
        

