from typing import Annotated
from app.db import model, schemas
from app.db.db_conn import get_db
from sqlalchemy.sql import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes.current_user import get_current_user
from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy import outerjoin  # Import this for outer join

router = APIRouter(tags=["Player's Profile"])

@router.get("/player/profiles")
async def player_profile(sess: Annotated[AsyncSession, Depends(get_db)], user: model.Player = Depends(get_current_user)):
    try:
        stmt = (
            select(model.Player, model.PlayerStats)
            .select_from(model.Player)
            .outerjoin(model.PlayerStats)
            .where(model.Player.id == user.id)
        )
        result = await sess.execute(stmt)
        player_row = result.one_or_none()  

        if player_row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crediential Expire. Please login again")

        player, stats = player_row  

        # Handle None stats by defaulting to 0
        runs = stats.runs if stats else 0
        balls_faced = stats.balls_faced if stats else 0
        wickets = stats.wickets if stats else 0
        overs_bowled = stats.overs_bowled if stats else 0.0
        runs_conceded = stats.runs_conceded if stats else 0

        # Calculate strike rates safely
        batting_sr = (runs / balls_faced * 100) if balls_faced > 0 else 0.0
        bowling_sr = (overs_bowled * 6 / wickets) if wickets > 0 else 0.0

        return {
            'id': player.id,
            'name': player.name,
            'photo_url': player.photo_url,
            'category': player.category,
            'runs': runs, 
            'batting_strike_rate': batting_sr,  
            'wickets': wickets,  
            'bowling_strike_rate': bowling_sr,  
            'overs_bowled': overs_bowled,
            'total_runs_conceded': runs_conceded  
        }
    except HTTPException as e:
        print(e)
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")
    