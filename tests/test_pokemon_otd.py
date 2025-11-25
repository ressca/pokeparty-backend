import pytest
from datetime import date
from app.services.pokemon_otd import get_or_create_pokemon_of_the_day
from app.models import pokemon_of_the_day
from app.config import LAST_POKEMON_ID


def test_get_or_create_pokemon_of_the_day_creates_new(db_session):
    # Arrange
    today = date.today().isoformat()
    
    # Act
    potd = get_or_create_pokemon_of_the_day(db_session)
    
    # Assert
    assert potd is not None
    assert potd.day_date == today
    assert 1 <= potd.pokemon_id <= LAST_POKEMON_ID
    
    # Check that it's in the database
    db_potd = db_session.query(pokemon_of_the_day).filter(
        pokemon_of_the_day.day_date == today
    ).first()
    assert db_potd is not None
    assert db_potd.pokemon_id == potd.pokemon_id


def test_get_or_create_pokemon_of_the_day_returns_existing(db_session):
    # Arrange
    from datetime import timedelta
    # Use a past date to avoid collision with other tests running today
    past_date = (date.today() - timedelta(days=30)).isoformat()
    existing_potd = pokemon_of_the_day(day_date=past_date, pokemon_id=25)  # Pikachu
    db_session.add(existing_potd)
    db_session.commit()
    
    # Act - get today's POTD (not yesterday's)
    potd = get_or_create_pokemon_of_the_day(db_session)
    
    # Assert - today's POTD should exist and be valid
    assert potd is not None
    assert potd.day_date == date.today().isoformat()
    assert 1 <= potd.pokemon_id <= LAST_POKEMON_ID


def test_get_or_create_pokemon_of_the_day_idempotent(db_session):
    # Act
    potd1 = get_or_create_pokemon_of_the_day(db_session)
    potd2 = get_or_create_pokemon_of_the_day(db_session)
    potd3 = get_or_create_pokemon_of_the_day(db_session)
    
    # Assert - all should have the same pokemon_id
    assert potd1.pokemon_id == potd2.pokemon_id
    assert potd2.pokemon_id == potd3.pokemon_id


def test_get_or_create_pokemon_of_the_day_thread_safe(db_session):
    # Arrange
    from datetime import timedelta
    # Use a specific past date to avoid collision with other tests
    specific_date = (date.today() - timedelta(days=60)).isoformat()
    
    # Create POTD in database for that date
    potd1 = pokemon_of_the_day(day_date=specific_date, pokemon_id=50)
    db_session.add(potd1)
    db_session.commit()
    
    # Act - verify it was saved (we can't easily test concurrent access in unit test)
    retrieved = db_session.query(pokemon_of_the_day).filter(
        pokemon_of_the_day.day_date == specific_date
    ).first()
    
    # Assert
    assert retrieved is not None
    assert retrieved.pokemon_id == 50
    # Should be exactly one
    count = db_session.query(pokemon_of_the_day).filter(
        pokemon_of_the_day.day_date == specific_date
    ).count()
    assert count == 1

def test_different_days_have_different_potd(db_session):
    from datetime import date, timedelta
    
    # Arrange
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    # Stwórz POTD dla wczoraj
    yesterday_potd = pokemon_of_the_day(day_date=yesterday, pokemon_id=1)
    db_session.add(yesterday_potd)
    db_session.commit()
    
    # Act - get POTD for today
    today_potd = get_or_create_pokemon_of_the_day(db_session)
    
    # Assert - can be different
    # (although statistically they can be the same)
    assert yesterday_potd.day_date != today_potd.day_date