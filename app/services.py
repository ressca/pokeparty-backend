from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
import random
from . import models
from .config import LAST_POKEMON_ID

def get_or_create_pokemon_of_the_day(db: Session) -> models.pokemon_of_the_day:
    """
    Retrieves the Pokemon of the Day for the current date.
    If it doesn't exist, it randomly selects one and saves it to the database.
    Thread-safe thanks to database unique constraints.
    """
    today = date.today().isoformat()

    # 1. Try to find existing entry for today
    existing_potd = db.query(models.pokemon_of_the_day).filter(
        models.pokemon_of_the_day.day_date == today
    ).first()

    if existing_potd:
        return existing_potd

    # 2. If not found, create a new one
    random_pokemon_id = random.randint(1, LAST_POKEMON_ID)
    
    new_potd = models.pokemon_of_the_day(
        day_date=today,
        pokemon_id=random_pokemon_id
    )

    try:
        db.add(new_potd)
        db.commit()
        db.refresh(new_potd)
        return new_potd
    except IntegrityError:
        db.rollback()
        return db.query(models.pokemon_of_the_day).filter(
            models.pokemon_of_the_day.day_date == today
        ).first()
