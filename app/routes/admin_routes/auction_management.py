from typing import List, Annotated
from datetime import datetime
from app.db import model, schemas
from sqlalchemy.orm import aliased
from app.db.db_conn import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.routes.boardcast import auction_state
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException, status


router = APIRouter(tags=['Auction_Management'])


#3. =================================== AUCTION MANAGEMENT ======================================
# """Select players for auction in a tournament"""
@router.post("/auction/select-players", status_code=status.HTTP_201_CREATED)
async def select_players_for_auction(tournament_id: int,player_ids: List[int],sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
        tournament_result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == tournament_id)
        )
        tournament = tournament_result.scalar_one_or_none()
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        players_result = await sess.execute(
            select(model.Player).filter(model.Player.id.in_(player_ids))
        )
        players = players_result.scalars().all()
        if len(players) != len(player_ids):
            raise HTTPException(status_code=400, detail="No players is not found")
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
    except HTTPException:
        raise
    except Exception:
        await sess.rollback()
        raise HTTPException(status_code=500, detail="Failed to select players for auction")



#2. Get all auction players for a particular tournament:
@router.get("/auction/tournaments/{tournament_id}/players", response_model=List[schemas.AuctionPlayerResponse])
async def get_auction_players(tournament_id: int,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
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
                player_id=ap.player_id if ap else None,
                tournament_id=ap.tournament_id if ap else None,
                start_players=ap.start_players if ap else None,
                category= p.category if ap else None, 
                base_price=ap.base_price if ap else None,
                sold_price=ap.sold_price if ap else None,
                sold_to_team_id=ap.sold_to_team_id if ap else None,
                player_name=p.name if p else None,
                team_name=t.team_name if t else None
            ) for ap, p, t in auction_data
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch auction players")


#3. Ready player for auction/ update:
@router.put("/auction/prepared-player/{auction_player_id}")
async def prepared_player_for_auction(auction_player_id: int,auction_update: schemas.AuctionPlayerBioUpdate,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
        result = await sess.execute(
            select(model.AuctionPlayer).filter(model.AuctionPlayer.id == auction_player_id)
        )
        auction_player = result.scalar_one_or_none()
        if not auction_player:
            raise HTTPException(status_code=404, detail="Auction player not found")
        auction_player.start_players = auction_update.start_players
        auction_player.base_price = auction_update.base_price
        await sess.commit()
        return {"message": "Player information update successfully"}
    except HTTPException:
        raise
    except Exception:
        await sess.rollback()
        raise HTTPException(status_code=500, detail="Failed to prepare player for auction")



#4. Assign a player to a team during auction/ update a auction player information:
@router.put("/auction/assign-player/{auction_player_id}")
async def assign_player_to_team(auction_player_id: int,auction_update: schemas.AuctionPlayerUpdate,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
        result = await sess.execute(
            select(model.AuctionPlayer).filter(model.AuctionPlayer.id == auction_player_id)
        )
        auction_player = result.scalar_one_or_none()
        if not auction_player:
            raise HTTPException(status_code=404, detail="Auction player not found")
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
            raise HTTPException(status_code=404, detail="Team or plyaer is not found or doesn't belong to this tournament")
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
        if count >= 40:
            raise HTTPException(status_code=400, detail="Team already has maximum 30 players")
        auction_player.sold_to_team_id = auction_update.sold_to_team_id
        auction_player.sold_price = auction_update.sold_price
        team.current_conis -= auction_update.sold_price
        await sess.commit()
        player_team_result = await sess.execute(
            select(model.Player, model.Team)
            .select_from(model.Player)
            .join(model.Team, model.Team.id == auction_update.sold_to_team_id)
            .filter(model.Player.id == auction_player.player_id)
        )
        player, team = player_team_result.first()
        if auction_state.is_live:
            assignment_data = {
                "type": "player_assigned",
                "player_id": player.id,
                "player_name": player.name,
                "team_id": team.id,
                "team_name": team.team_name,
                "sold_price": auction_update.sold_price,
                "assigned_at": datetime.now().isoformat()
            }
            await auction_state.broadcast(assignment_data)
        return {"message": "Player assigned to team successfully or player update successfully"}
    except HTTPException:
        raise
    except Exception:
        await sess.rollback()
        raise HTTPException(status_code=500, detail="Failed to assign player to team")
    
    

# ==================================== Availablility, Remove =========================================
# 1. Get all players available for auction (not already selected):
@router.get("/players/available-for-auction")
async def get_available_players_for_auction(tournament_id: int,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
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
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch available players")
        
        



#2. """Remove a player from auction (if not sold yet)"""
@router.delete("/auction/remove-player/{auction_player_id}")
async def remove_player_from_auction(auction_player_id: int,sess: Annotated[AsyncSession, Depends(get_db)],current_admin: model.Player = Depends(get_current_admin_user)):
    try:
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
    except HTTPException:
        raise
    except Exception:
        await sess.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove player from auction")
            
            

    
