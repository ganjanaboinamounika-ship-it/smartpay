from app.core.security import hash_password
from app.models import User, UserRole


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["role"] == "CUSTOMER"


def test_duplicate_email_registration(client):
    data = {
        "email": "duplicate@example.com",
        "password": "Password123"
    }

    first = client.post("/api/v1/auth/register", json=data)
    second = client.post("/api/v1/auth/register", json=data)

    assert first.status_code == 201
    assert second.status_code == 409


def test_successful_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "Password123"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_invalid_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid@example.com",
            "password": "Password123"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid@example.com",
            "password": "WrongPass123"
        }
    )

    assert response.status_code == 401


def test_inactive_user_login(client, db_session):
    user = User(
        email="inactive@example.com",
        password_hash=hash_password("Password123"),
        role=UserRole.CUSTOMER,
        is_active=False,
    )

    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "Password123"
        }
    )

    assert response.status_code == 403


def test_get_current_user(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "Password123"
        }
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "me@example.com",
            "password": "Password123"
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_get_current_user_without_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401