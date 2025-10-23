import enum 
from typing import Annotated
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
        print(value)
        print(type(value))
        print(PlayerCategory.batter)
        print(type(PlayerCategory.batter))
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

    
    
    