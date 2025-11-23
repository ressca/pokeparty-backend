from app.services import get_or_create_pokemon_of_the_day
from app.models import pokemon_of_the_day
from datetime import date


def test_get_or_create_pokemon_of_the_day_gets_existing(db_session):
    # First call - creates the entry
    potd1 = get_or_create_pokemon_of_the_day(db_session)
    
    # Second call - should return the SAME entry
    potd2 = get_or_create_pokemon_of_the_day(db_session)

    today = date.today().isoformat()

    assert potd1.id == potd2.id
    assert potd1.pokemon_id == potd2.pokemon_id
    assert potd1.day_date == potd2.day_date == today

    # Verify only one entry exists in DB
    count = db_session.query(pokemon_of_the_day).count()
    assert count == 1
