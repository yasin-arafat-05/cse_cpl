import enum 
from typing import Annotated
from datetime import datetime,timezone
from pydantic import BaseModel,EmailStr,Field
from pydantic import field_validator


class PlayerCategory(enum.Enum):
    batter = "batter"
    bowler = "bowler"
    all_rounder = "all_rounder"
    wicket_keeper = "wicket_keeper"
    

class CreateUser(BaseModel):
    email : Annotated[EmailStr,Field(...)]
    password : Annotated[str,Field(...,min_length=6,description="password must be greather than 6 chars")]
    name : Annotated[str,Field(description="User Name")]
    category : Annotated[str,Field(description="Player category (batter, bowler, all_rounder, wicket_keeper)")]
    
    @field_validator('category',mode="after")
    @classmethod
    def validator(cls,value):
        # print(value)
        # print(type(value))
        # print(PlayerCategory.batter)
        # print(type(PlayerCategory.batter))
        if value not in ["batter","bowler","all_rounder","wicket_keeper"]:
            raise ValueError("category field value is not correct")
        return value 
    
    
class USERME(BaseModel):
    email : str
    id : int 
    
    
    
class EmailSchema(BaseModel):
    emails : list[str]
    
    
    
class Token(BaseModel):
    access_token: str
    token_type: str


# Admin Schemas
class TournamentCreate(BaseModel):
    name: str
    year: int
    start_date : str  = datetime.now(timezone.utc).isoformat()
    end_date: str  = datetime.now(timezone.utc).isoformat()
    
class TournamentResponse(BaseModel):
    id: int
    name: str
    year: int
    status: str
    start_date: str
    end_date: str
    created_at: str

class TeamCreate(BaseModel):
    tournament_id: int
    team_name: str
    team_code: str

class TeamResponse(BaseModel):
    id: int
    tournament_id: int
    team_name: str
    team_code: str
    logo_url: str
    created_at: str

class AuctionPlayerCreate(BaseModel):
    player_id: int
    tournament_id: int
    base_price: float = 20.00

class AuctionPlayerUpdate(BaseModel):
    sold_price: float
    sold_to_team_id: int

class AuctionPlayerResponse(BaseModel):
    id: int
    player_id: int
    tournament_id: int
    start_players: bool
    base_price: float
    sold_price: float
    sold_to_team_id: int
    player_name: str
    team_name: str = None

class MatchCreate(BaseModel):
    tournament_id: int
    team1_id: int
    team2_id: int
    match_date: str  
    venue: str

class MatchResponse(BaseModel):
    id: int
    tournament_id: int
    team1_id: int
    team2_id: int
    match_date: str
    venue: str
    created_at: str
    team1_name: str
    team2_name: str

class MatchStatsCreate(BaseModel):
    match_id: int
    man_of_the_match: int
    winner_team: int

class MatchStatsResponse(BaseModel):
    id: int
    match_id: int
    man_of_the_match: int
    winner_team: int
    man_of_the_match_name: str
    winner_team_name: str

class TeamPlayerCount(BaseModel):
    team_id: int
    team_name: str
    player_count: int
    max_players: int = 30
    
    