import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
from app.models import PopularityLeaderboard, ComparisonSession


def test_get_all_popularity(client, db_session):
    # Arrange
    db_session.add(PopularityLeaderboard(pokemon_id=1, elo=1000))
    db_session.add(PopularityLeaderboard(pokemon_id=2, elo=1050))
    db_session.add(PopularityLeaderboard(pokemon_id=3, elo=950))
    db_session.commit()
    
    # Act
    response = client.get("/popularity/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["pokemon_id"] == 1
    assert data[0]["elo"] == 1000


def test_get_specific_pokemon_popularity(client, db_session):
    # Arrange
    db_session.add(PopularityLeaderboard(pokemon_id=5, elo=1234))
    db_session.commit()
    
    # Act
    response = client.get("/popularity/5")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["pokemon_id"] == 5
    assert data["elo"] == 1234


def test_get_pokemon_not_found(client):
    response = client.get("/popularity/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_top_n_popularity(client, db_session):
    # Arrange
    for i in range(1, 6):
        db_session.add(PopularityLeaderboard(pokemon_id=i, elo=1000 + (i * 100)))
    db_session.commit()
    
    # Act
    response = client.get("/popularity/top/3")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    # Should be in descending order of ELO
    assert data[0]["elo"] > data[1]["elo"]
    assert data[1]["elo"] > data[2]["elo"]


def test_get_pair_to_battle(client, db_session):
    # Act
    response = client.get("/popularity/pair-to-battle")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "pokemon1_id" in data
    assert "pokemon2_id" in data
    assert "session_id" in data
    assert data["pokemon1_id"] != data["pokemon2_id"]
    # IDs should be between 1 and LAST_POKEMON_ID
    assert 1 <= data["pokemon1_id"]
    assert 1 <= data["pokemon2_id"]
    
    # Check that session is in the database
    session = db_session.query(ComparisonSession).filter_by(
        session_id=data["session_id"]
    ).first()
    assert session is not None
    assert session.pokemon1_id == data["pokemon1_id"]
    assert session.pokemon2_id == data["pokemon2_id"]


def test_vote_pokemon1_wins(client, db_session):
    # Arrange - create a pair
    response = client.get("/popularity/pair-to-battle")
    session_id = response.json()["session_id"]
    pokemon1_id = response.json()["pokemon1_id"]
    pokemon2_id = response.json()["pokemon2_id"]
    
    # Act - vote for pokemon1
    vote_response = client.post(f"/popularity/vote/{session_id}/{pokemon1_id}")
    
    # Assert
    assert vote_response.status_code == status.HTTP_200_OK
    # Session should be deleted
    session = db_session.query(ComparisonSession).filter_by(
        session_id=session_id
    ).first()
    assert session is None


def test_vote_pokemon2_wins(client, db_session):
    # Arrange
    response = client.get("/popularity/pair-to-battle")
    session_id = response.json()["session_id"]
    pokemon1_id = response.json()["pokemon1_id"]
    pokemon2_id = response.json()["pokemon2_id"]
    
    # Act - vote for pokemon2
    vote_response = client.post(f"/popularity/vote/{session_id}/{pokemon2_id}")
    
    # Assert
    assert vote_response.status_code == status.HTTP_200_OK
    data = vote_response.json()
    assert data["pokemon1_id"] == pokemon1_id
    assert data["pokemon2_id"] == pokemon2_id


def test_vote_invalid_session(client):
    response = client.post("/popularity/vote/invalid-session-id/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_vote_expired_session(client, db_session):
    # Arrange - create an expired session
    expired_session = ComparisonSession(
        session_id="expired-session",
        pokemon1_id=1,
        pokemon2_id=2,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    )
    db_session.add(expired_session)
    db_session.commit()
    
    # Act
    response = client.post("/popularity/vote/expired-session/1")
    
    # Assert
    assert response.status_code == status.HTTP_410_GONE


def test_vote_invalid_pokemon_id(client, db_session):
    # Arrange
    response = client.get("/popularity/pair-to-battle")
    session_id = response.json()["session_id"]
    
    # Act - vote for Pokemon outside the pair
    vote_response = client.post(f"/popularity/vote/{session_id}/9999")
    
    # Assert
    assert vote_response.status_code == status.HTTP_400_BAD_REQUEST


def test_vote_updates_elo(client, db_session):
    # Act - Get a random pair first
    pair_response = client.get("/popularity/pair-to-battle")
    assert pair_response.status_code == status.HTTP_200_OK
    
    data = pair_response.json()
    session_id = data["session_id"]
    pokemon1_id = data["pokemon1_id"]
    pokemon2_id = data["pokemon2_id"]
    
    # Arrange - Ensure these Pokemon exist in leaderboard with known ELO
    # We check if they exist and update/create them
    p1 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=pokemon1_id).first()
    if not p1:
        p1 = PopularityLeaderboard(pokemon_id=pokemon1_id, elo=1000)
        db_session.add(p1)
    else:
        p1.elo = 1000
        
    p2 = db_session.query(PopularityLeaderboard).filter_by(pokemon_id=pokemon2_id).first()
    if not p2:
        p2 = PopularityLeaderboard(pokemon_id=pokemon2_id, elo=1000)
        db_session.add(p2)
    else:
        p2.elo = 1000
        
    db_session.commit()
    
    # Act - Vote for pokemon1
    vote_response = client.post(f"/popularity/vote/{session_id}/{pokemon1_id}")
    assert vote_response.status_code == status.HTTP_200_OK
    
    # Assert - check that ELO changed
    db_session.refresh(p1)
    db_session.refresh(p2)
    
    # One should have more ELO, the other less
    assert p1.elo != 1000 or p2.elo != 1000
