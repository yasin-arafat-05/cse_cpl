from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.db.db_conn import asyncSession
from app.db import model, schemas
from app.routes.current_user import get_current_admin_user

router = APIRouter(tags=['Admin'])



#1.==================================== TOURNAMENT MANAGEMENT =======================================
## 1. Create a new tournament:
@router.post("/tournaments/create", response_model=schemas.TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(tournament: schemas.TournamentCreate,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        # Convert string dates to date objects
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
        

# 2. Get all tournaments:
@router.get("/tournaments/fetch", response_model=List[schemas.TournamentResponse])
async def get_tournaments(current_admin: model.Player = Depends(get_current_admin_user)):
    """Get all tournaments"""
    async with asyncSession() as sess:
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

# 3. Update Tournaments Status to -> upcoming, active, completed
@router.put("/tournaments/{tournament_id}/status")
async def update_tournament_status(tournament_id: int,new_status: str,current_admin: model.Player = Depends(get_current_admin_user)):
    if new_status not in ['upcoming', 'active', 'completed']:
        raise HTTPException(status_code=400, detail="Invalid status. Must be: upcoming, active, or completed")
    
    async with asyncSession() as sess:
        result = await sess.execute(select(model.Tournament).filter(model.Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        tournament.status = new_status
        await sess.commit()
        return {"message": f"Tournament status updated to {new_status}"}
    
    

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





#3. =================================== AUCTION MANAGEMENT ======================================
@router.post("/auction/select-players", status_code=status.HTTP_201_CREATED)
async def select_players_for_auction(
    tournament_id: int,
    player_ids: List[int],
    current_admin: model.Player = Depends(get_current_admin_user)
):
    """Select players for auction in a tournament"""
    async with asyncSession() as sess:
        # Check if tournament exists
        tournament_result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == tournament_id)
        )
        tournament = tournament_result.scalar_one_or_none()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        # Check if players exist
        players_result = await sess.execute(
            select(model.Player).filter(model.Player.id.in_(player_ids))
        )
        players = players_result.scalars().all()
        
        if len(players) != len(player_ids):
            raise HTTPException(status_code=400, detail="Some players not found")
        
        # Create auction players (initially not sold to any team)
        auction_players = []
        for player_id in player_ids:
            auction_player = model.AuctionPlayer(
                player_id=player_id,
                tournament_id=tournament_id,
                sold_to_team_id=None,
                sold_price=0.0
            )
            auction_players.append(auction_player)
        
        sess.add_all(auction_players)
        await sess.commit()
        
        return {"message": f"Selected {len(player_ids)} players for auction"}

#2. Get all auction players for a tournament:
@router.get("/auction/tournaments/{tournament_id}/players", response_model=List[schemas.AuctionPlayerResponse])
async def get_auction_players(tournament_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        result = await sess.execute(
            select(model.AuctionPlayer, model.Player, model.Team)
            .join(model.Player, model.AuctionPlayer.player_id == model.Player.id)
            .outerjoin(model.Team, model.AuctionPlayer.sold_to_team_id == model.Team.id)
            .filter(model.AuctionPlayer.tournament_id == tournament_id)
        )
        auction_data = result.all()
        return [
            schemas.AuctionPlayerResponse(
                id=ap.id,
                player_id=ap.player_id,
                tournament_id=ap.tournament_id,
                start_players=ap.start_players,
                base_price=ap.base_price,
                sold_price=ap.sold_price,
                sold_to_team_id=ap.sold_to_team_id,
                player_name=p.name,
                team_name=t.team_name if t else None
            ) for ap, p, t in auction_data
        ]

@router.put("/auction/assign-player/{auction_player_id}")
async def assign_player_to_team(
    auction_player_id: int,
    auction_update: schemas.AuctionPlayerUpdate,
    current_admin: model.Player = Depends(get_current_admin_user)
):
    """Assign a player to a team during auction"""
    async with asyncSession() as sess:
        # Get auction player
        result = await sess.execute(
            select(model.AuctionPlayer).filter(model.AuctionPlayer.id == auction_player_id)
        )
        auction_player = result.scalar_one_or_none()
        
        if not auction_player:
            raise HTTPException(status_code=404, detail="Auction player not found")
        
        # Check if team exists and belongs to the same tournament
        team_result = await sess.execute(
            select(model.Team).filter(
                and_(
                    model.Team.id == auction_update.sold_to_team_id,
                    model.Team.tournament_id == auction_player.tournament_id
                )
            )
        )
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found or doesn't belong to this tournament")
        # Check team player limit (30 players max)
        current_players_count = await sess.execute(
            select(func.count(model.AuctionPlayer.id))
            .filter(
                and_(
                    model.AuctionPlayer.sold_to_team_id == auction_update.sold_to_team_id,
                    model.AuctionPlayer.tournament_id == auction_player.tournament_id,
                    model.AuctionPlayer.sold_to_team_id.isnot(None)
                )
            )
        )
        count = current_players_count.scalar()
        if count >= 30:
            raise HTTPException(status_code=400, detail="Team already has maximum 30 players")
        # Update auction player
        auction_player.sold_to_team_id = auction_update.sold_to_team_id
        auction_player.sold_price = auction_update.sold_price
        
        await sess.commit()
        
        return {"message": "Player assigned to team successfully"}

@router.get("/teams/{team_id}/player-count", response_model=schemas.TeamPlayerCount)
async def get_team_player_count(
    team_id: int,
    current_admin: model.Player = Depends(get_current_admin_user)
):
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



# ====================================== MATCH MANAGEMENT =====================================================
#  1. Create a new match:
@router.post("/matches", response_model=schemas.MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(match: schemas.MatchCreate,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        # Check if tournament exists
        tournament_result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == match.tournament_id)
        )
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
        match_date = datetime.strptime(match.match_date, "%Y-%m-%d %H:%M:%S")
        
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
    async with asyncSession() as sess:
        result = await sess.execute(
            select(model.Match, model.Team, model.Team)
            .join(model.Team, model.Match.team1_id == model.Team.id, aliased=True)
            .join(model.Team, model.Match.team2_id == model.Team.id, aliased=True)
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
async def get_team_player_distribution(tournament_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        result = await sess.execute(
            select(
                model.Team.id,
                model.Team.team_name,
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
            .group_by(model.Team.id, model.Team.team_name)
        )
        
        team_distributions = result.all()
        
        return [
            {
                "team_id": team_id,
                "team_name": team_name,
                "player_count": player_count,
                "max_players": 30,
                "available_slots": 30 - player_count
            }
            for team_id, team_name, player_count in team_distributions
        ]



# ==================================== UTILITY ENDPOINTS =========================================
# 1. Get all players available for auction (not already selected):
@router.get("/players/available-for-auction")
async def get_available_players_for_auction(tournament_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        # Get players not already in auction for this tournament
        result = await sess.execute(
            select(model.Player)
            .filter(
                and_(
                    model.Player.is_active == True,
                    ~model.Player.id.in_(
                        select(model.AuctionPlayer.player_id)
                        .filter(model.AuctionPlayer.tournament_id == tournament_id)
                    )
                )
            )
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
        
        


#2. """Remove a player from auction (if not sold yet)"""
@router.delete("/auction/remove-player/{auction_player_id}")
async def remove_player_from_auction(auction_player_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    
    async with asyncSession() as sess:
        result = await sess.execute(
            select(model.AuctionPlayer).filter(model.AuctionPlayer.id == auction_player_id)
        )
        auction_player = result.scalar_one_or_none()
        
        if not auction_player:
            raise HTTPException(status_code=404, detail="Auction player not found")
        
        if auction_player.sold_to_team_id is not None:
            raise HTTPException(status_code=400, detail="Cannot remove sold player from auction")
        
        await sess.delete(auction_player)
        await sess.commit()
        
        return {"message": "Player removed from auction successfully"}
            
            
            
            