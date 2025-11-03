from datetime import datetime
from app.db import model, schemas
from typing import List,Annotated
from sqlalchemy.orm import aliased
from sqlalchemy import select, func, and_
from app.db.db_conn import get_db
from app.routes.boardcast import auction_state
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status


router = APIRouter(tags=['Admin'])


# === 5. Get the a perticular team with all the team - member: ===
@router.get("/teams/{team_id}/player-count", response_model=schemas.TeamPlayerCount)
async def get_team_player_count(team_id: int,sess = Annotated[AsyncSession,Depends(get_db)], current_admin: model.Player = Depends(get_current_admin_user)):
    try:
        team_result = await sess.execute(select(model.Team).filter(model.Team.id == team_id))
        team = team_result.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        count_result = await sess.execute(
                select(func.count(model.AuctionPlayer.id))
                .filter(
                    and_(
                        model.AuctionPlayer.sold_to_team_id == team_id,
                        model.AuctionPlayer.sold_to_team_id.isnot(None)
                    )
                )
        )
        player_count = count_result.scalar()
        return schemas.TeamPlayerCount(
            team_id=team.id,
            team_name=team.team_name,
            player_count=player_count,
            max_players=30
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch team player count")




# ======================== DASHBOARD & ANALYTICS ========================
# 1. Get comprehensive overview of a tournament"""
@router.get("/dashboard/tournaments/{tournament_id}/overview")
async def get_tournament_overview(tournament_id: int,sess = Annotated[AsyncSession,Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
        tournament_result = await sess.execute(
                select(model.Tournament).filter(model.Tournament.id == tournament_id)
            )
        tournament = tournament_result.scalar_one_or_none()
        if not tournament:
                raise HTTPException(status_code=404, detail="Tournament not found")
        teams_count_result = await sess.execute(
                select(func.count(model.Team.id))
                .filter(model.Team.tournament_id == tournament_id)
            )
        teams_count = teams_count_result.scalar()
        matches_count_result = await sess.execute(
                select(func.count(model.Match.id))
                .filter(model.Match.tournament_id == tournament_id))
        matches_count = matches_count_result.scalar()
        auction_players_count_result = await sess.execute(
                select(func.count(model.AuctionPlayer.id))
                .filter(model.AuctionPlayer.tournament_id == tournament_id)
            )
        auction_players_count = auction_players_count_result.scalar()
        sold_players_count_result = await sess.execute(
                select(func.count(model.AuctionPlayer.id))
                .filter(
                    and_(
                        model.AuctionPlayer.tournament_id == tournament_id,
                        model.AuctionPlayer.sold_to_team_id.isnot(None)
                    )
                )
            )
        sold_players_count = sold_players_count_result.scalar()
        return {
                "tournament": {
                    "id": tournament.id,
                    "name": tournament.name,
                    "year": tournament.year,
                    "status": tournament.status,
                    "start_date": str(tournament.start_date),
                    "end_date": str(tournament.end_date)
                },
                "statistics": {
                    "total_teams": teams_count,
                    "total_matches": matches_count,
                    "total_auction_players": auction_players_count,
                    "sold_players": sold_players_count,
                    "unsold_players": auction_players_count - sold_players_count
                }
            }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch tournament overview")



#2.Get player distribution across teams in a tournament:
@router.get("/dashboard/teams/{tournament_id}/player-distribution")
async def get_team_player_distribution(tournament_id: int,sess = Annotated[AsyncSession,Depends(get_db)]):
        try:
            result = await sess.execute(
                select(
                    model.Team.id,
                    model.Team.team_name,
                    model.Team.conis,
                    func.count(model.AuctionPlayer.id).label('player_count')
                )
                .outerjoin(
                    model.AuctionPlayer,
                    and_(
                        model.AuctionPlayer.sold_to_team_id == model.Team.id,
                        model.AuctionPlayer.sold_to_team_id.isnot(None)
                    )
                )
                .filter(model.Team.tournament_id == tournament_id)
                .group_by(model.Team.id, model.Team.team_name,model.Team.conis)
            )
            team_distributions = result.all()
            return [
                {
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_coin" : coins,
                    "player_count": player_count,
                    "max_players": 30,
                    "available_slots": 30 - player_count
                }
                for team_id, team_name, coins ,player_count in team_distributions
            ]
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to fetch player distribution")



            