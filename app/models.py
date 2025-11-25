from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username: str = Column(String, unique=True, index=True, nullable=False)
    email: str = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    profile_pic_pokemon_id: int = Column(Integer, nullable=True)

    favorite_pokemons = relationship("favorite_pokemon", back_populates="user", cascade="all, delete-orphan")


class favorite_pokemon(Base):
    __tablename__ = 'favorite_pokemons'

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    pokemon_id: int = Column(Integer, nullable=False)

    user = relationship("User", back_populates="favorite_pokemons")


class pokemon_of_the_day(Base):
    __tablename__ = 'pokemon_of_the_day'

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day_date: str = Column(String, index=True, unique=True, nullable=False)
    pokemon_id: int = Column(Integer, nullable=False)


class PopularityLeaderboard(Base):
    __tablename__ = "popularity_leaderboard"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pokemon_id: int = Column(Integer, nullable=False, index=True)
    elo: int = Column(Integer, nullable=False)


class ComparisonSession(Base):
    __tablename__ = "comparison_sessions"

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id: str = Column(String, unique=True, index=True, nullable=False)
    pokemon1_id: int = Column(Integer, nullable=False)
    pokemon2_id: int = Column(Integer, nullable=False)
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at: datetime = Column(DateTime, nullable=False)
