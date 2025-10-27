
#""" 
# This is Boardcast:
# Not Multicast:
# Only 1 auction can be live in the 
#"""
import json
from app.db import model
from sqlalchemy.sql import select
from fastapi.requests import Request
from sqlalchemy.orm import selectinload
from app.db.db_conn import asyncSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,HTMLResponse
from app.routes.current_user import get_current_admin_user
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status,Depends

router = APIRouter(tags=['Auction-Live'])

templates = Jinja2Templates(directory="app/internal/html/")

class AuctionState:
    def __init__(self):
        self.is_live = False
        self.active_tournament = None
        self.active_connections = []
    
    def start_live(self, tournament_id):
        self.is_live = True
        self.active_tournament = tournament_id
    
    def stop_live(self):
        self.is_live = False
        self.active_tournament = None
    
    async def add_connection(self, websocket):
        if self.is_live:
            await websocket.accept()
            self.active_connections.append(websocket)
            return True
        return False
    
    def remove_connection(self, websocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message):
        if self.is_live:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting: {e}")
                    disconnected.append(connection)
            # Remove disconnected clients
            for connection in disconnected:
                self.remove_connection(connection)
                
auction_state = AuctionState()



# ====================Go-Live For A Pariticular Tounament====================
@router.post("/auction/go-live/{tournament_id}")
async def start_live_auction(tournament_id: int,current_admin: model.Player = Depends(get_current_admin_user)):
    async with asyncSession() as sess:
        # Check if tournament exists or not:
        result = await sess.execute(
            select(model.Tournament).filter(model.Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
    
    auction_state.start_live(tournament_id)
    return {"message": f"Auction for tournament {tournament_id} is now LIVE!"}
   
   
# ================= Stop Live =========================
@router.post("/auction/stop-live")
async def stop_live_auction(
    current_admin: model.Player = Depends(get_current_admin_user)
):
    # Broadcast ending message
    await auction_state.broadcast({
        "type": "auction_ended",
        "message": "Auction has ended"
    })
    auction_state.stop_live()
    return {"message": "Auction stopped"}
    

# For Controlling the Live Button Brother.
@router.get("/auction/status")
async def get_auction_status():
    status =  {
        "is_live": auction_state.is_live,
        "active_tournament": auction_state.active_tournament
    }
    return status
    
    
    

# ==================== web socket:) ====================
@router.websocket("/ws/auction/live")
async def websocket_auction_live(websocket: WebSocket):
   
    # Only accept connection if auction is live
    connected = await auction_state.add_connection(websocket)
    
    if not connected:
        await websocket.close(code=1000, reason="Auction is not live")
        return
    
    try:
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to live auction",
            "tournament_id": auction_state.active_tournament
        })
        
        # Keep connection alive
        while auction_state.is_live:
            # Wait for any message (just to keep connection alive)
            data = await websocket.receive_text()
            # You can process any client messages here if needed
            
    except WebSocketDisconnect:
        auction_state.remove_connection(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        auction_state.remove_connection(websocket)
        
        