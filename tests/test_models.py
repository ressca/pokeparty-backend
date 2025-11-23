from app.models import User, favorite_pokemon, pokemon_of_the_day

def test_create_user(db_session):
    # Create a user
    new_user = User(username="testuser", email="test@example.com", hashed_password="secretpassword")
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    
    # Check if the user was saved and has an ID assigned
    assert new_user.id is not None
    assert new_user.username == "testuser"
    assert new_user.email == "test@example.com"

def test_favorite_pokemon_relationship(db_session):
    # Create a user
    user = User(username="ash", email="ash@ketchum.com", hashed_password="pika")
    db_session.add(user)
    db_session.commit()
    
    # Add a favorite pokemon
    fav = favorite_pokemon(user_id=user.id, pokemon_id=25)
    db_session.add(fav)
    db_session.commit()
    
    # Check the relationship from the favorite_pokemon object perspective
    assert fav.user_id == user.id
    assert fav.user.username == "ash"
    
    # Check the relationship from the User object perspective (back_populates)
    # Refresh the user object to load the relationship
    db_session.refresh(user)
    assert len(user.favorite_pokemons) == 1
    assert user.favorite_pokemons[0].pokemon_id == 25

def test_pokemon_of_the_day(db_session):
    from datetime import date
    # Test the Pokemon of the Day model with dynamic date
    today_str = date.today().isoformat()
    potd = pokemon_of_the_day(day_date=today_str, pokemon_id=150)
    db_session.add(potd)
    db_session.commit()
    
    assert potd.id is not None
    assert potd.day_date == today_str
    assert potd.pokemon_id == 150
