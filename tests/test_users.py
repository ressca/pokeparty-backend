from fastapi import status
import pytest

# Helper to get token
def get_auth_header(client, username="testuser", password="password123"):
    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password}
    )
    response = client.post(
        "/auth/token",
        data={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_current_user(client):
    headers = get_auth_header(client)
    response = client.get("/users/current-user", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"

def test_update_user_profile(client):
    headers = get_auth_header(client)
    
    # Update profile pic
    response = client.patch(
        "/users/update",
        json={"profile_pic_pokemon_id": 25},
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["profile_pic_pokemon_id"] == 25
    
    # Verify persistence
    response = client.get("/users/current-user", headers=headers)
    assert response.json()["profile_pic_pokemon_id"] == 25

def test_update_user_invalid_pokemon_id(client):
    headers = get_auth_header(client)
    response = client.patch(
        "/users/update",
        json={"profile_pic_pokemon_id": 9999},
        headers=headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_add_and_remove_favorite_pokemon(client):
    headers = get_auth_header(client)
    
    # Add favorite
    response = client.post(
        "/users/favorite-pokemon",
        json={"pokemon_id": 1},
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # Get favorites
    response = client.get("/users/favorite-pokemons", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["pokemon_id"] == 1

    # Remove favorite
    # Note: The endpoint expects a body with pokemon_id, not a path parameter
    response = client.request(
        "DELETE",
        "/users/favorite-pokemon/",
        json={"pokemon_id": 1},
        headers=headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify removal
    response = client.get("/users/favorite-pokemons", headers=headers)
    assert len(response.json()) == 0
    

def test_delete_user(client):
    headers = get_auth_header(client)
    
    # Delete user
    response = client.delete("/users/me", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify user is gone (token should be invalid or user not found)
    # Actually, the token might still be valid signature-wise, but get_current_user checks DB.
    response = client.get("/users/current-user", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
