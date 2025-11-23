from fastapi import status

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_email(client):
    client.post(
        "/auth/register",
        json={"username": "user1", "email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/register",
        json={"username": "user2", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_409_CONFLICT

def test_login_user(client):
    # Register first
    client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    
    # Login
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
