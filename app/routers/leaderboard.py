from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import popularity_leaderboard
from ..schemas import PopularityLeaderboardCreate, PopularityLeaderboard

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("/", response_model=List[PopularityLeaderboard])
def get_all(db: Session = Depends(get_db)):
    return db.query(popularity_leaderboard).all()

@router.post("/", response_model=PopularityLeaderboard)
def create(entry: PopularityLeaderboardCreate, db: Session = Depends(get_db)):
    obj = popularity_leaderboard(pokemon_id=entry.pokemon_id, elo=entry.elo)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{entry_id}", response_model=PopularityLeaderboard)
def get(entry_id: int, db: Session = Depends(get_db)):
    obj = db.query(popularity_leaderboard).filter_by(id=entry_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Entry not found")
    return obj
