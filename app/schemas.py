from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from .config import LAST_POKEMON_ID

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)

class UserResponse(UserBase):
    id: int
    profile_pic_pokemon_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    email: Optional[EmailStr] = None
    profile_pic_pokemon_id: Optional[int] = Field(None, ge=1, le=LAST_POKEMON_ID)


# --- Favorite Pokemon Schemas ---
class FavoritePokemonBase(BaseModel):
    pokemon_id: int = Field(..., ge=1, le=LAST_POKEMON_ID)

class FavoritePokemonCreate(FavoritePokemonBase):
    pass

class FavoritePokemon(FavoritePokemonBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class FavoritePokemonDelete(FavoritePokemonBase):
    pass


class PopularityLeaderboardBase(BaseModel):
    pokemon_id: int
    elo: int

class PopularityLeaderboardCreate(PopularityLeaderboardBase):
    pass

class PopularityLeaderboard(PopularityLeaderboardBase):
    id: int

    class Config:
        orm_mode = True
