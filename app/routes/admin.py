from typing import List
from datetime import datetime
from app.db import model, schemas
from sqlalchemy.orm import aliased
from app.db.db_conn import asyncSession
from sqlalchemy import select, func, and_
from app.routes.boardcast import auction_state
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(tags=['Admin'])


# === 5. Get the a perticular team with all the team - member: ===
@router.get("/teams/{team_id}/player-count", response_model=schemas.TeamPlayerCount)
async def get_team_player_count(team_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    """Get player count for a specific team"""
    async with asyncSession() as sess:
        # Get team info
        team_result = await sess.execute(select(model.Team).filter(model.Team.id == team_id))
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Count players
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




# ======================== DASHBOARD & ANALYTICS ========================
# 1. Get comprehensive overview of a tournament"""
@router.get("/dashboard/tournaments/{tournament_id}/overview")
async def get_tournament_overview(tournament_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    
    # Get tournament info
    async with asyncSession() as sess:
        tournament_result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == tournament_id)
        )
        tournament = tournament_result.scalar_one_or_none()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        # Get teams count
        teams_count_result = await sess.execute(
            select(func.count(model.Team.id))
            .filter(model.Team.tournament_id == tournament_id)
        )
        teams_count = teams_count_result.scalar()
        
        
        # Get matches count
        matches_count_result = await sess.execute(
            select(func.count(model.Match.id))
            .filter(model.Match.tournament_id == tournament_id))
        matches_count = matches_count_result.scalar()
        
        # Get auction players count
        auction_players_count_result = await sess.execute(
            select(func.count(model.AuctionPlayer.id))
            .filter(model.AuctionPlayer.tournament_id == tournament_id)
        )
        auction_players_count = auction_players_count_result.scalar()
        
        # Get sold players count
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



#2.Get player distribution across teams in a tournament:
@router.get("/dashboard/teams/{tournament_id}/player-distribution")
async def get_team_player_distribution(tournament_id: int):
    async with asyncSession() as sess:
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
        print(team_distributions)
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



            