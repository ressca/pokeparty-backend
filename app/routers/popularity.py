from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import PopularityLeaderboard
from ..schemas import PopularityLeaderboardCreate, PopularityLeaderboard as PopularityLeaderboardSchema

router = APIRouter(
    prefix="/popularity",
    tags=["Popularity"]
)

@router.get("/", response_model=List[PopularityLeaderboardSchema])
def get_all(db: Session = Depends(get_db)):
    return db.query(PopularityLeaderboard).all()

@router.post("/", response_model=PopularityLeaderboardSchema)
def create(entry: PopularityLeaderboardCreate, db: Session = Depends(get_db)):
    obj = PopularityLeaderboard(pokemon_id=entry.pokemon_id, elo=entry.elo)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{entry_id}", response_model=PopularityLeaderboardSchema)
def get(entry_id: int, db: Session = Depends(get_db)):
    obj = db.query(PopularityLeaderboard).filter_by(id=entry_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Entry not found")
    return obj
