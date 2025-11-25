from sqlalchemy.orm import Session
from ..models import PopularityLeaderboard


def update_elo_and_save(db: Session, pokemon1_id: int, pokemon2_id: int, winner_pokemon_id: int):
    # Validate winner_pokemon_id
    if winner_pokemon_id not in [pokemon1_id, pokemon2_id]:
        raise ValueError("Winner ID must be one of the pokemon IDs")
    
    K_FACTOR = 48
    
    pokemon1 = db.query(PopularityLeaderboard).filter_by(pokemon_id=pokemon1_id).first()
    if not pokemon1:
        pokemon1 = PopularityLeaderboard(pokemon_id=pokemon1_id, elo=1000)
        db.add(pokemon1)
        db.commit()
    
    pokemon2 = db.query(PopularityLeaderboard).filter_by(pokemon_id=pokemon2_id).first()
    if not pokemon2:
        pokemon2 = PopularityLeaderboard(pokemon_id=pokemon2_id, elo=1000)
        db.add(pokemon2)
        db.commit()
    
    pokemon1_won = winner_pokemon_id == pokemon1_id
    
    expected_1 = 1 / (1 + 10 ** ((pokemon2.elo - pokemon1.elo) / 400))
    expected_2 = 1 / (1 + 10 ** ((pokemon1.elo - pokemon2.elo) / 400))
    
    result_1 = 1 if pokemon1_won else 0
    result_2 = 0 if pokemon1_won else 1
    
    new_elo_1 = pokemon1.elo + K_FACTOR * (result_1 - expected_1)
    new_elo_2 = pokemon2.elo + K_FACTOR * (result_2 - expected_2)
    
    pokemon1.elo = int(new_elo_1)
    pokemon2.elo = int(new_elo_2)
    
    db.add(pokemon1)
    db.add(pokemon2)
    db.commit()
