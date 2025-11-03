
from typing import List
from app.db import model, schemas
from typing import Annotated
from app.db.db_conn import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status



router = APIRouter(tags=['Admin-Team-Management'])


# =============================== TEAM MANAGEMENT ==============================================
#1. Create a new team under a tournament
@router.post("/teams", response_model=schemas.TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team: schemas.TeamCreate,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
        try:
            tournament_result = await sess.execute(
                select(model.Tournament).filter(model.Tournament.id == team.tournament_id)
            )
            tournament = tournament_result.scalar_one_or_none()
            if not tournament:
                raise HTTPException(status_code=404, detail="Tournament not found")
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
        except HTTPException:
            raise
        except Exception:
            await sess.rollback()
            raise HTTPException(status_code=500, detail="Failed to create team")


# 2. =====================<>=================<>===================<>===============<>=============
@router.get("/tournaments/{tournament_id}/teams", response_model=List[schemas.TeamWithPlayersResponse])
async def get_teams_with_players(tournament_id: int,sess: Annotated[AsyncSession, Depends(get_db)]):
        try:
            result = await sess.execute(
                select(model.Team).filter(model.Team.tournament_id == tournament_id)
            )
            teams = result.scalars().all()
            if not teams:
                raise HTTPException(status_code=404, detail="No teams found for this tournament")
            response = []
            for team in teams:
                ap_result = await sess.execute(
                    select(model.AuctionPlayer)
                    .options(selectinload(model.AuctionPlayer.players))
                    .filter(model.AuctionPlayer.tournament_id == tournament_id)
                    .filter(model.AuctionPlayer.sold_to_team_id == team.id)
                )
                auction_players = ap_result.scalars().all()
                players = [
                    schemas.PlayerResponse(
                        id=ap.player_id,
                        name=ap.players.name,
                        email=ap.players.email,
                        category=ap.players.category.value,
                        photo_url=ap.players.photo_url
                    )
                    for ap in auction_players
                ]
                team_data = schemas.TeamWithPlayersResponse(
                    id=team.id,
                    team_name=team.team_name,
                    team_code=team.team_code,
                    players=players
                )
                response.append(team_data)
            return response
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to fetch teams with players")


# 3. ===================<>=================<>===================<>===============<>=============
# =============================== Add Coin Team ================================================
@router.post('/update/team/coin/{tounament_id}/{team_id}')
async def update_team_coin(tounament_id,team_id,new_coin,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
        try:
            result = await sess.execute(
                select(model.Team).filter(
                    and_(
                    model.Team.tournament_id == tounament_id,
                    model.Team.id == team_id
                  )
                )
            )
            team = result.scalar_one_or_none()
            if not team:
                raise HTTPException(status_code=404, detail="No teams found for this tournament")
            team.conis += new_coin
            await sess.commit()
            return {f"coin update successfull"}
        except HTTPException:
            raise
        except Exception:
            await sess.rollback()
            raise HTTPException(status_code=500, detail="Failed to update team coin")
        
        
    


