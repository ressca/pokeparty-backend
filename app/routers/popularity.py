from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import PopularityLeaderboard, ComparisonSession
from ..schemas import PopularityBattlePair, PopularityLeaderboard as PopularityLeaderboardSchema
import random
from ..config import LAST_POKEMON_ID
import uuid
from ..services.ranking import update_elo_and_save
from datetime import datetime, timedelta, timezone
from ..services.ranking import update_elo_and_save


router = APIRouter(
    prefix="/popularity",
    tags=["Popularity"]
)

@router.get("/", response_model=List[PopularityLeaderboardSchema])
def get_all(db: Session = Depends(get_db)):
    return db.query(PopularityLeaderboard).all()


@router.get("/pair-to-battle", response_model=PopularityBattlePair)
def get_pair_to_battle(db: Session = Depends(get_db)):
    random1 = random.randint(1, LAST_POKEMON_ID)
    random2 = random.randint(1, LAST_POKEMON_ID)
    while random2 == random1:
        random2 = random.randint(1, LAST_POKEMON_ID)

    session_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    session = ComparisonSession(
        session_id=session_id,
        pokemon1_id=random1,
        pokemon2_id=random2,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()

    return {"pokemon1_id": random1, "pokemon2_id": random2, "session_id": session_id}


@router.get("/top/{n}", response_model=List[PopularityLeaderboardSchema])
def get_top_n(n: int, db: Session = Depends(get_db)):
    return db.query(PopularityLeaderboard).order_by(PopularityLeaderboard.elo.desc()).limit(n).all()


@router.get("/{pokemon_id}", response_model=PopularityLeaderboardSchema)
def get(pokemon_id: int, db: Session = Depends(get_db)):
    obj = db.query(PopularityLeaderboard).filter_by(pokemon_id=pokemon_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Pokemon not found in the leaderboard")
    return obj


@router.post("/vote/{session_id}/{winner_pokemon_id}", response_model=PopularityBattlePair)
def vote(session_id: str, winner_pokemon_id: int, db: Session = Depends(get_db)):
    session = db.query(ComparisonSession).filter_by(session_id=session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if datetime.now(timezone.utc).replace(tzinfo=None) > session.expires_at:
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=410, detail="Session expired")

    pokemon1_id = session.pokemon1_id
    pokemon2_id = session.pokemon2_id

    if winner_pokemon_id not in [pokemon1_id, pokemon2_id]:
        raise HTTPException(status_code=400, detail="Winner pokemon ID does not match the battle pair")

    update_elo_and_save(db, pokemon1_id, pokemon2_id, winner_pokemon_id)
    
    db.delete(session)
    db.commit()

    return {"pokemon1_id": pokemon1_id, "pokemon2_id": pokemon2_id, "session_id": session_id}