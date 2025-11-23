from pydantic import BaseModel, EmailStr, Field
from typing import Optional

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

    class Config:
        from_attributes = True
