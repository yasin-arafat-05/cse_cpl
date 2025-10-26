
from typing import List
from app.db import model, schemas
from app.db.db_conn import asyncSession
from sqlalchemy import select, func, and_
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status



router = APIRouter(tags=['Admin-Team-Management'])


#2.=============================== TEAM MANAGEMENT ==============================================
#1. Create a new team under a tournament
@router.post("/teams", response_model=schemas.TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team: schemas.TeamCreate,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        tournament_result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == team.tournament_id)
        )
        tournament = tournament_result.scalar_one_or_none()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        # Check if team code already exists in this tournament
        existing_team = await sess.execute(
            select(model.Team).filter(
                and_(
                    model.Team.tournament_id == team.tournament_id,
                    model.Team.team_code == team.team_code
                )
            )
        )
        if existing_team.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Team code already exists in this tournament")
        
        new_team = model.Team(
            tournament_id=team.tournament_id,
            team_name=team.team_name,
            team_code=team.team_code
        )
        
        sess.add(new_team)
        await sess.commit()
        await sess.refresh(new_team)
        
        return schemas.TeamResponse(
            id=new_team.id,
            tournament_id=new_team.tournament_id,
            team_name=new_team.team_name,
            team_code=new_team.team_code
        )

#2. Get all teams for a specific tournament: 
@router.get("/tournaments/{tournament_id}/teams", response_model=List[schemas.TeamResponse])
async def get_teams_by_tournament(tournament_id: int, current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        result = await sess.execute(
            select(model.Team).filter(model.Team.tournament_id == tournament_id))
        teams = result.scalars().all()
        return [
            schemas.TeamResponse(
                id=t.id,
                tournament_id=t.tournament_id,
                team_name=t.team_name,
                team_code=t.team_code,
                logo_url=t.logo_url,
                created_at=str(t.created_at)
            ) for t in teams
        ]


