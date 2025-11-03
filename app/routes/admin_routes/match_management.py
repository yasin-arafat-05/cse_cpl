from typing import List
from datetime import datetime
from app.db import model, schemas
from sqlalchemy.orm import aliased
from app.db.db_conn import asyncSession
from sqlalchemy import select, func, and_
from app.routes.boardcast import auction_state
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status


router = APIRouter(tags=['Match_Management'])


# ====================================== MATCH MANAGEMENT =====================================================
#  1. Create a new match:
@router.post("/matches", response_model=schemas.MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(match: schemas.MatchCreate,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        # Check if tournament exists
        tournament_result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == match.tournament_id))
        tournament = tournament_result.scalar_one_or_none()
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        # Check if teams exist and belong to the tournament
        teams_result = await sess.execute(
            select(model.Team).filter(
                and_(
                    model.Team.id.in_([match.team1_id, match.team2_id]),
                    model.Team.tournament_id == match.tournament_id
                )
            )
        )
        teams = teams_result.scalars().all()
        
        if len(teams) != 2:
            raise HTTPException(status_code=400, detail="Teams not found or don't belong to this tournament")
        
        # Convert string date to datetime
        match_date = datetime.fromisoformat(match.match_date).date()
        
        new_match = model.Match(
            tournament_id=match.tournament_id,
            team1_id=match.team1_id,
            team2_id=match.team2_id,
            match_date=match_date,
            venue=match.venue
        )
        
        sess.add(new_match)
        await sess.commit()
        await sess.refresh(new_match)
        
        # Get team names for response
        team1_name = next(t.team_name for t in teams if t.id == match.team1_id)
        team2_name = next(t.team_name for t in teams if t.id == match.team2_id)
        
        return schemas.MatchResponse(
            id=new_match.id,
            tournament_id=new_match.tournament_id,
            team1_id=new_match.team1_id,
            team2_id=new_match.team2_id,
            match_date=str(new_match.match_date),
            venue=new_match.venue,
            created_at=str(new_match.created_at),
            team1_name=team1_name,
            team2_name=team2_name
        )

# 2.  Get all matches for a specific tournament:
@router.get("/tournaments/{tournament_id}/matches", response_model=List[schemas.MatchResponse])
async def get_matches_by_tournament(tournament_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    TEAM1 = aliased(model.Team,name='team1')
    TEAM2 = aliased(model.Team,name='team2')
    async with asyncSession() as sess:
        result = await sess.execute(
            select(model.Match, TEAM1,TEAM2)
            .join(TEAM1, model.Match.team1_id == TEAM1.id)
            .join(TEAM2, model.Match.team2_id == TEAM2.id)
            .filter(model.Match.tournament_id == tournament_id))
        matches_data = result.all()
        return [
            schemas.MatchResponse(
                id=m.id,
                tournament_id=m.tournament_id,
                team1_id=m.team1_id,
                team2_id=m.team2_id,
                match_date=str(m.match_date),
                venue=m.venue,
                created_at=str(m.created_at),
                team1_name=t1.team_name,
                team2_name=t2.team_name
            ) for m, t1, t2 in matches_data
        ]

# 3. Create match statistics after a match is completed:
@router.post("/match-stats", response_model=schemas.MatchStatsResponse, status_code=status.HTTP_201_CREATED)
async def create_match_stats(match_stats: schemas.MatchStatsCreate,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        # Check if match exists
        match_result = await sess.execute(
            select(model.Match).filter(model.Match.id == match_stats.match_id)
        )
        match = match_result.scalar_one_or_none()
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Check if man of the match player exists
        player_result = await sess.execute(
            select(model.Player).filter(model.Player.id == match_stats.man_of_the_match)
        )
        player = player_result.scalar_one_or_none()
        
        if not player:
            raise HTTPException(status_code=404, detail="Man of the match player not found")
        
        # Check if winner team exists and belongs to the same tournament
        team_result = await sess.execute(
            select(model.Team).filter(
                and_(
                    model.Team.id == match_stats.winner_team,
                    model.Team.tournament_id == match.tournament_id
                )
            )
        )
        winner_team = team_result.scalar_one_or_none()
        
        if not winner_team:
            raise HTTPException(status_code=404, detail="Winner team not found or doesn't belong to this tournament")
        
        # Check if match stats already exists for this match
        existing_stats = await sess.execute(
            select(model.MatchStats).filter(model.MatchStats.match_id == match_stats.match_id)
        )
        if existing_stats.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Match stats already exist for this match")
        
        # Create match stats
        new_match_stats = model.MatchStats(
            match_id=match_stats.match_id,
            man_of_the_match=match_stats.man_of_the_match,
            winner_team=match_stats.winner_team
        )
        
        sess.add(new_match_stats)
        await sess.commit()
        await sess.refresh(new_match_stats)
        
        return schemas.MatchStatsResponse(
            id=new_match_stats.id,
            match_id=new_match_stats.match_id,
            man_of_the_match=new_match_stats.man_of_the_match,
            winner_team=new_match_stats.winner_team,
            man_of_the_match_name=player.name,
            winner_team_name=winner_team.team_name
        )


#4. Get match statistics for a specific match:
@router.get("/matches/{match_id}/stats", response_model=schemas.MatchStatsResponse)
async def get_match_stats(match_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        result = await sess.execute(
            select(model.MatchStats, model.Player, model.Team)
            .join(model.Player, model.MatchStats.man_of_the_match == model.Player.id)
            .join(model.Team, model.MatchStats.winner_team == model.Team.id)
            .filter(model.MatchStats.match_id == match_id)
        )
        
        match_stats_data = result.first()
        
        if not match_stats_data:
            raise HTTPException(status_code=404, detail="Match stats not found")
        
        ms, player, team = match_stats_data
        
        return schemas.MatchStatsResponse(
            id=ms.id,
            match_id=ms.match_id,
            man_of_the_match=ms.man_of_the_match,
            winner_team=ms.winner_team,
            man_of_the_match_name=player.name,
            winner_team_name=team.team_name
        )


