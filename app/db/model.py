import enum
from datetime import datetime
from app.db.db_conn import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey


#______________enum_____________
class PlayerCategory(enum.Enum):
    batter = "batter"
    bowler = "bowler"
    all_rounder = "all_rounder"
    wicket_keeper = "wicket_keeper"

class UserRole(enum.Enum):
    player = "player"
    admin = "admin"


# ---------------------------------------------------------------------
# _______________________________ Table _______________________________
# ---------------------------------------------------------------------

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer,index=True, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    photo_url = Column(String(500), default='app/photo/player/default.png')
    
    # bowler,batter,all_rounder
    #category = Column(Enum(PlayerCategory), nullable=False)#enum reques a name 
    category = Column(Enum(PlayerCategory,name="player_category"), nullable=False) 
    
    # admin,player
    role = Column(Enum(UserRole,name="user_role"), default=UserRole.player)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    player_stats = relationship("PlayerStats", back_populates="players",cascade="all, delete-orphan")
    match_stats = relationship("MatchStats", back_populates="players",cascade="all, delete-orphan")
    auction_players = relationship("AuctionPlayer", back_populates="players",cascade="all, delete-orphan")
    



class PlayerStats(Base):
    __tablename__ = 'player_stats'
    
    id = Column(Integer,index=True, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))

    # Batting Stats
    runs = Column(Integer, default=0)
    balls_faced = Column(Integer, default=0)
    
    # Bowling Stats
    wickets = Column(Integer, default=0)
    overs_bowled = Column(Float(4, 1), default=0.0)
    runs_conceded = Column(Integer, default=0)
    
    # Relationships
    players = relationship("Player",back_populates="player_stats")
    



class Tournament(Base):
    __tablename__ = 'tournaments'
    
    id = Column(Integer,index=True, primary_key=True)
    name = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum('upcoming', 'active', 'completed',name="status"), default='upcoming')
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=func.now())
    
    # relationship:)
    matches = relationship("Match", back_populates="tournaments",cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="tournaments",cascade="all, delete-orphan")
    auction_players = relationship("AuctionPlayer", back_populates="tournaments",cascade="all, delete-orphan")


class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer,index=True, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    team_name = Column(String(100), nullable=False)
    team_code = Column(String(100),default=None)
    logo_url = Column(String(255),default=None)
    created_at = Column(DateTime, default=func.now())
    
    # relationship:)
    auction_players = relationship("AuctionPlayer", back_populates="teams",cascade="all, delete-orphan")
    match_stats = relationship("MatchStats", back_populates="teams",cascade="all, delete-orphan")
    team1 = relationship("Match",foreign_keys="Match.team1_id", back_populates="team1",cascade="all, delete-orphan")
    team2 = relationship("Match",foreign_keys="Match.team2_id", back_populates="team2",cascade="all, delete-orphan")
    tournaments = relationship("Tournament",back_populates="teams")
 

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer,index=True,primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    team1_id = Column(Integer, ForeignKey('teams.id'))
    team2_id = Column(Integer, ForeignKey('teams.id'))
    match_date = Column(DateTime)
    venue = Column(String(100),default=None)
    created_at = Column(DateTime, default=func.now())
    
    # relationship:)
    match_stats = relationship("MatchStats", back_populates="matches",cascade="all, delete-orphan")
    tournaments = relationship("Tournament", back_populates="matches")
    team1 = relationship("Team",foreign_keys=[team1_id],back_populates="team1")
    team2 = relationship("Team",foreign_keys=[team2_id],back_populates="team2")
 

class MatchStats(Base):
    __tablename__ = "match_stats"
    id = Column(Integer,index=True,primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    man_of_the_match = Column(Integer, ForeignKey("players.id"), nullable=False)
    winner_team = Column(Integer, ForeignKey('teams.id'))
    
    # relationship:
    matches = relationship("Match",back_populates="match_stats")    
    players = relationship("Player",back_populates="match_stats")
    teams = relationship("Team",back_populates="match_stats")



class AuctionPlayer(Base):
    __tablename__ = 'auction_players'
    id = Column(Integer,index=True, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    start_players = Column(String(2),default='Z')
    base_price = Column(Float(12, 2), default=20.00)
    sold_price = Column(Float(12, 2), default=0.00)
    sold_to_team_id = Column(Integer, ForeignKey('teams.id'),nullable=True)

    #relationship:) 
    players = relationship("Player",back_populates="auction_players")
    tournaments = relationship("Tournament",back_populates="auction_players")
    teams = relationship("Team",back_populates="auction_players")
    
    
