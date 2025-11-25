import pytest
from app.models import PopularityLeaderboard
from app.services.ranking import update_elo_and_save


def test_update_elo_and_save_pokemon1_wins(db_session):
    # Arrange - create two Pokemon with ELO 1000
    # Use unique IDs to avoid collision with other tests
    p1_id, p2_id = 2001, 2002
    pokemon1 = PopularityLeaderboard(pokemon_id=p1_id, elo=1000)
    pokemon2 = PopularityLeaderboard(pokemon_id=p2_id, elo=1000)
    db_session.add(pokemon1)
    db_session.add(pokemon2)
    db_session.commit()
    
    # Act - pokemon1 wins
    update_elo_and_save(db_session, pokemon1_id=p1_id, pokemon2_id=p2_id, winner_pokemon_id=p1_id)
    
    # Assert - pokemon1 should have more ELO, pokemon2 less
    updated_pokemon1 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p1_id).first()
    updated_pokemon2 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p2_id).first()
    
    # With K=48, gain is 24. 1000 -> 1024
    assert updated_pokemon1.elo > 1000
    assert updated_pokemon2.elo < 1000
    # Sum should remain the same (ELO transfer)
    assert abs((updated_pokemon1.elo + updated_pokemon2.elo) - 2000) < 0.1


def test_update_elo_and_save_pokemon2_wins(db_session):
    # Arrange
    p1_id, p2_id = 2003, 2004
    pokemon1 = PopularityLeaderboard(pokemon_id=p1_id, elo=1200)
    pokemon2 = PopularityLeaderboard(pokemon_id=p2_id, elo=800)
    db_session.add(pokemon1)
    db_session.add(pokemon2)
    db_session.commit()
    
    # Act - pokemon2 wins (unexpected win, more points)
    update_elo_and_save(db_session, pokemon1_id=p1_id, pokemon2_id=p2_id, winner_pokemon_id=p2_id)
    
    # Assert
    updated_pokemon1 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p1_id).first()
    updated_pokemon2 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p2_id).first()
    
    assert updated_pokemon1.elo < 1200
    assert updated_pokemon2.elo > 800


def test_update_elo_creates_missing_pokemon(db_session):
    # Act - compare Pokemon that don't exist in the database
    p1_id, p2_id = 2100, 2101
    update_elo_and_save(db_session, pokemon1_id=p1_id, pokemon2_id=p2_id, winner_pokemon_id=p1_id)
    
    # Assert - should be created with initial ELO
    pokemon1 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p1_id).first()
    pokemon2 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p2_id).first()
    
    assert pokemon1 is not None
    assert pokemon2 is not None
    assert pokemon1.elo > 1000  # Won
    assert pokemon2.elo < 1000  # Lost


def test_elo_calculation_expected_winner(db_session):
    # Arrange - favorite vs underdog
    p1_id, p2_id = 2005, 2006
    favorite = PopularityLeaderboard(pokemon_id=p1_id, elo=1400)
    underdog = PopularityLeaderboard(pokemon_id=p2_id, elo=600)
    db_session.add(favorite)
    db_session.add(underdog)
    db_session.commit()
    
    favorite_elo_before = favorite.elo
    underdog_elo_before = underdog.elo
    
    # Act - favorite wins (expected)
    update_elo_and_save(db_session, pokemon1_id=p1_id, pokemon2_id=p2_id, winner_pokemon_id=p1_id)
    
    # Assert
    updated_favorite = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p1_id).first()
    updated_underdog = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p2_id).first()
    
    favorite_gain = updated_favorite.elo - favorite_elo_before
    underdog_loss = underdog_elo_before - updated_underdog.elo
    
    # Favorite gets fewer points (with K=48: ~0.48 points, rounded to 0)
    # So we allow 0 gain
    assert 0 <= favorite_gain < 3
    # Underdog loses little (with K=48: ~0.48 points, rounded to 0)
    assert 0 <= underdog_loss < 3


def test_elo_calculation_underdog_wins(db_session):
    # Arrange
    p1_id, p2_id = 2007, 2008
    favorite = PopularityLeaderboard(pokemon_id=p1_id, elo=1400)
    underdog = PopularityLeaderboard(pokemon_id=p2_id, elo=600)
    db_session.add(favorite)
    db_session.add(underdog)
    db_session.commit()
    
    underdog_elo_before = underdog.elo
    
    # Act - underdog wins (unexpected)
    update_elo_and_save(db_session, pokemon1_id=p1_id, pokemon2_id=p2_id, winner_pokemon_id=p2_id)
    
    # Assert
    updated_underdog = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=p2_id).first()
    
    underdog_gain = updated_underdog.elo - underdog_elo_before
    
    # Underdog gets many points (with K=48: ~47 points)
    assert underdog_gain > 30


def test_update_elo_invalid_winner_id(db_session):
    p1_id, p2_id = 2009, 2010
    pokemon1 = PopularityLeaderboard(pokemon_id=p1_id, elo=1000)
    pokemon2 = PopularityLeaderboard(pokemon_id=p2_id, elo=1000)
    db_session.add(pokemon1)
    db_session.add(pokemon2)
    db_session.commit()
    
    # Act & Assert - should raise ValueError
    with pytest.raises(ValueError):
        update_elo_and_save(db_session, pokemon1_id=p1_id, pokemon2_id=p2_id, winner_pokemon_id=999)