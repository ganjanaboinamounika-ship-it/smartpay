from types import SimpleNamespace

import app.services.payment_verification_service as verification_service


def register_and_login(client, email="paymentuser@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_test_payment(client, token, key="payment-key-001", amount="100.00"):
    return client.post(
        "/api/v1/payments/create",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": key,
        },
        json={
            "amount": amount,
            "currency": "INR",
            "payment_method": "UPI",
        },
    )


def test_create_payment(client):
    token = register_and_login(client)

    response = create_test_payment(client, token)

    assert response.status_code == 201
    assert response.json()["amount"] == "100.00"
    assert response.json()["currency"] == "INR"
    assert response.json()["status"] == "PENDING"


def test_missing_idempotency_key(client):
    token = register_and_login(client)

    response = client.post(
        "/api/v1/payments/create",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": "100.00",
            "currency": "INR",
            "payment_method": "UPI",
        },
    )

    assert response.status_code == 422


def test_invalid_idempotency_key(client):
    token = register_and_login(client)

    response = create_test_payment(
        client,
        token,
        key="bad key!!",
    )

    assert response.status_code == 400


def test_same_idempotency_key_returns_original_payment(client):
    token = register_and_login(client)

    first = create_test_payment(client, token)
    second = create_test_payment(client, token)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["transaction_id"] == second.json()["transaction_id"]


def test_different_details_with_same_key_returns_conflict(client):
    token = register_and_login(client)

    first = create_test_payment(
        client, token, amount="100.00"
    )

    second = create_test_payment(
        client, token, amount="500.00"
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_payment_verification_success(client, monkeypatch):
    token = register_and_login(client)
    payment = create_test_payment(client, token)

    payment_id = payment.json()["id"]

    monkeypatch.setattr(
        verification_service,
        "record_transaction_and_count",
        lambda **kwargs: 1,
    )

    monkeypatch.setattr(
        verification_service,
        "dispatch_webhook_deliveries",
        lambda deliveries: None,
    )

    response = client.post(
        "/api/v1/payments/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "payment_id": payment_id,
            "gateway_status": "SUCCESS",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["gateway_transaction_id"] is not None


def test_payment_verification_failed(client, monkeypatch):
    token = register_and_login(client)
    payment = create_test_payment(client, token)

    monkeypatch.setattr(
        verification_service,
        "record_transaction_and_count",
        lambda **kwargs: 1,
    )

    monkeypatch.setattr(
        verification_service,
        "dispatch_webhook_deliveries",
        lambda deliveries: None,
    )

    response = client.post(
        "/api/v1/payments/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "payment_id": payment.json()["id"],
            "gateway_status": "FAILED",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"


def test_payment_verification_timeout(client, monkeypatch):
    token = register_and_login(client)
    payment = create_test_payment(client, token)

    monkeypatch.setattr(
        verification_service,
        "record_transaction_and_count",
        lambda **kwargs: 1,
    )

    monkeypatch.setattr(
        verification_service,
        "dispatch_webhook_deliveries",
        lambda deliveries: None,
    )

    response = client.post(
        "/api/v1/payments/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "payment_id": payment.json()["id"],
            "gateway_status": "TIMEOUT",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"


def test_high_risk_payment_is_rejected(client, monkeypatch):
    token = register_and_login(client)
    payment = create_test_payment(client, token)

    monkeypatch.setattr(
        verification_service,
        "record_transaction_and_count",
        lambda **kwargs: 1,
    )

    monkeypatch.setattr(
        verification_service,
        "evaluate_payment",
        lambda **kwargs: SimpleNamespace(
            total_score=85,
            risk_level="HIGH",
        ),
    )

    monkeypatch.setattr(
        verification_service,
        "dispatch_webhook_deliveries",
        lambda deliveries: None,
    )

    response = client.post(
        "/api/v1/payments/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "payment_id": payment.json()["id"],
            "gateway_status": "SUCCESS",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "FAILED"
    assert response.json()["fraud_score"] == 85
    assert response.json()["risk_level"] == "HIGH"


def test_get_payment(client):
    token = register_and_login(client)
    payment = create_test_payment(client, token)

    response = client.get(
        f"/api/v1/payments/{payment.json()['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == payment.json()["id"]


def test_user_cannot_access_another_users_payment(client):
    token1 = register_and_login(client, "user1@example.com")
    token2 = register_and_login(client, "user2@example.com")

    payment = create_test_payment(client, token1)

    response = client.get(
        f"/api/v1/payments/{payment.json()['id']}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


def test_payment_not_found(client):
    token = register_and_login(client)

    response = client.get(
        "/api/v1/payments/99999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404