"""Tests for user registration, login, JWT validation, and profile endpoints."""

def test_user_registration_success(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "securepassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert "password" not in data  # Ensure hashed password is not leaked


def test_duplicate_username_fails(client):
    # 'tester' is already seeded in fixture
    response = client.post(
        "/api/auth/register",
        json={"username": "tester", "password": "password456"},
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["error"]["message"]


def test_login_success_and_jwt_token(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "tester", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password_fails(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "tester", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["error"]["message"]


def test_get_current_user_profile(client):
    # Log in first
    login_resp = client.post(
        "/api/auth/login",
        json={"username": "tester", "password": "testpass123"},
    )
    token = login_resp.json()["access_token"]

    # Call /api/auth/me with bearer token
    me_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "tester"


def test_unauthenticated_request_fails(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
