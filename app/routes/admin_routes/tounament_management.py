from typing import List, Annotated
from datetime import datetime
from sqlalchemy import select
from app.db import model, schemas
from app.db.db_conn import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status



router = APIRouter(tags=['Admin_Tournamet_Management'])


#1.==================================== TOURNAMENT MANAGEMENT =======================================
## 1. Create a new tournament:
@router.post("/tournaments/create", response_model=schemas.TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(tournament: schemas.TournamentCreate,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
        try:
            start_date = datetime.fromisoformat(tournament.start_date).date()
            end_date = datetime.fromisoformat(tournament.end_date).date()
            new_tournament = model.Tournament(
                name=tournament.name,
                year=tournament.year,
                start_date=start_date,
                end_date=end_date,
                status='upcoming'
            )
            sess.add(new_tournament)
            await sess.commit()
            await sess.refresh(new_tournament)
            return schemas.TournamentResponse(
                id=new_tournament.id,
                name=new_tournament.name,
                year=new_tournament.year,
                status=new_tournament.status,
                start_date=str(new_tournament.start_date),
                end_date=str(new_tournament.end_date),
                created_at=str(new_tournament.created_at)
            )
        except Exception:
            await sess.rollback()
            raise HTTPException(status_code=500, detail="Failed to create tournament")
        

# 2. Get all tournaments:
@router.get("/tournaments/fetch", response_model=List[schemas.TournamentResponse])
async def get_tournaments(sess: Annotated[AsyncSession, Depends(get_db)]):
    try:
        result = await sess.execute(select(model.Tournament).order_by(model.Tournament.created_at.desc()))
        tournaments = result.scalars().all()
        return [
                schemas.TournamentResponse(
                    id=t.id,
                    name=t.name,
                    year=t.year,
                    status=t.status,
                    start_date=str(t.start_date) if t.start_date else "",
                    end_date=str(t.end_date) if t.end_date else "",
                    created_at=str(t.created_at)
                ) for t in tournaments
            ]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch tournaments")


# 3. Update Tournaments Status to -> upcoming, active, completed
@router.put("/tournaments/{tournament_id}/status")
async def update_tournament_status(tournament_id: int,new_status: str,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
        if new_status not in ['upcoming', 'active', 'completed']:
            raise HTTPException(status_code=400, detail="Invalid status. Must be: upcoming, active, or completed")
        result = await sess.execute(select(model.Tournament).filter(model.Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        tournament.status = new_status
        await sess.commit()
        return {"message": f"Tournament status updated to {new_status}"}
    except HTTPException:
        raise
    except Exception:
        await sess.rollback()
        raise HTTPException(status_code=500, detail="Failed to update tournament status")
    
