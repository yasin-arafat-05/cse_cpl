
from app.db import model
from typing import Annotated
from app.db.db_conn import get_db
from sqlalchemy.sql import select 
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas import PlayerStatisticsUpate
from fastapi import APIRouter,Depends,HTTPException,status
from app.routes.current_user import get_current_admin_user


router = APIRouter(tags=["Player_Score_Update"])


@router.put("/update/batting/info/{player_id}")
async def update_batting_info(player_id:int,update_info:PlayerStatisticsUpate,sess: Annotated[AsyncSession,Depends(get_db)],user=Depends(get_current_admin_user)):
        try:
            info = await sess.execute(
                select(model.PlayerStats).where(model.PlayerStats.player_id==player_id))
            player = info.scalar_one_or_none()
            if not player:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Player not found")
            player.runs  += update_info.runs,
            player.balls_faced  += update_info.balls_faced,
            player.wickets +=  update_info.wickets,
            player.runs_conceded +=  update_info.runs_conceded,
            player.overs_bowled += update_info.overs_bowled,
            total_overs = player.overs_bowled + update_info.overs_bowled
            total_balls = int(total_overs) * 6 + int(round((total_overs % 1) * 10))
            overs = total_balls // 6
            balls = total_balls % 6
            player.overs_bowled = float(f"{overs}.{balls}")
            await sess.commit()
            return {"message": "Player batting info updated successfully"}
        except HTTPException:
            raise
        except Exception:
            await sess.rollback()
            raise HTTPException(status_code=500, detail="Failed to update player info")
        
        
        
    