import enum 
from datetime import datetime,timezone
from typing import Annotated,Optional,List
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
    
    # <______email______>
    @field_validator('email',mode="after")
    @classmethod
    def validator_email(cls,value):
        host = str(value).split("@")[-1]
        if host not in ["cse.pstu.ac.bd"]:
            raise ValueError("Can't create a account without university email")
        return value 
    
    # <______category______>
    @field_validator('category',mode="after")
    @classmethod
    def validator_category(cls,value):
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

class AuctionPlayerCreate(BaseModel):
    player_id: int
    tournament_id: int
    base_price: float = 20.00


class AuctionPlayerBioUpdate(BaseModel):
    base_price : int = 20 
    start_players : str 
    @field_validator('start_players',mode='after')
    @classmethod
    def validator(cls,value):
        if len(value)>1:
            raise ValueError("Category must be,in one character like, 'A','B','C'")
        return value 
    
    

class AuctionPlayerUpdate(BaseModel):
    sold_price: Optional[float] = None 
    sold_to_team_id: Optional[int] = None 

    

class AuctionPlayerResponse(BaseModel):
    id: int
    player_id: int
    tournament_id: int
    start_players: Optional[str] = None 
    category : Optional[str] = None 
    base_price: Optional[float] = None 
    sold_price: Optional[float] = None 
    sold_to_team_id: Optional[int] = None 
    player_name: str 
    team_name: Optional[str] = None

class MatchCreate(BaseModel):
    tournament_id: int
    team1_id: int
    team2_id: int
    match_date: str  = datetime.now(timezone.utc).isoformat()
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
    
    
class PlayerResponse(BaseModel):
    id: int
    name: str
    email: str
    category: str
    photo_url: str | None

class TeamWithPlayersResponse(BaseModel):
    id: int
    team_name: str
    team_code: str | None
    players: List[PlayerResponse]
    
    
class PlayerStatisticsUpate(BaseModel):
    runs : Optional[int] = 0 
    balls_faced : Optional[int] = 0 
    wickets : Optional[int] = 0 
    overs_bowled : Optional[float] = 0
    runs_conceded : Optional[int] = 0
    
     
    
    