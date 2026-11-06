import app.api.v1.webhooks as webhook_api

from app.models import WebhookDelivery


def setup_webhook_user(client, email="webhookuser@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123",
        },
    )

    return login.json()["access_token"]


def create_endpoint(client, token, monkeypatch):
    monkeypatch.setattr(
        webhook_api,
        "validate_webhook_url",
        lambda url: None,
    )
    monkeypatch.setattr(
        webhook_api,
        "encrypt_webhook_secret",
        lambda secret: "test-encrypted-secret",
    )

    return client.post(
        "/api/v1/webhooks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "url": "https://example.com/webhook",
            "events": ["payment.success", "payment.failed"],
        },
    )


def create_payment_for_webhook(client, token):
    response = client.post(
        "/api/v1/payments/create",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "webhook-payment-001",
        },
        json={
            "amount": "250.00",
            "currency": "INR",
            "payment_method": "UPI",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_delivery(db_session, endpoint_id, payment_id, status="FAILED"):
    delivery = WebhookDelivery(
        event_id="evt_test_webhook_001",
        endpoint_id=endpoint_id,
        payment_id=payment_id,
        event_type="payment.success",
        payload={"payment_id": payment_id},
        status=status,
        attempts=5 if status == "FAILED" else 1,
        max_attempts=5,
    )

    db_session.add(delivery)
    db_session.commit()
    db_session.refresh(delivery)

    return delivery


def setup_webhook_delivery(client, db_session, monkeypatch):
    token = setup_webhook_user(client)

    endpoint_response = create_endpoint(
        client, token, monkeypatch
    )
    assert endpoint_response.status_code == 201

    payment = create_payment_for_webhook(client, token)

    delivery = create_delivery(
        db_session,
        endpoint_response.json()["id"],
        payment["id"],
    )

    return token, endpoint_response.json()["id"], delivery


def test_register_webhook(client, monkeypatch):
    token = setup_webhook_user(client)

    response = create_endpoint(client, token, monkeypatch)

    assert response.status_code == 201
    assert response.json()["url"] == "https://example.com/webhook"
    assert response.json()["is_active"] is True
    assert response.json()["secret"]


def test_invalid_webhook_url(client, monkeypatch):
    token = setup_webhook_user(client)

    def reject_url(url):
        raise ValueError("Webhook URL must use HTTPS")

    monkeypatch.setattr(
        webhook_api,
        "validate_webhook_url",
        reject_url,
    )

    response = client.post(
        "/api/v1/webhooks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "url": "http://example.com/webhook",
            "events": ["payment.success"],
        },
    )

    assert response.status_code == 400


def test_duplicate_webhook_events_rejected(client):
    token = setup_webhook_user(client)

    response = client.post(
        "/api/v1/webhooks",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "url": "https://example.com/webhook",
            "events": ["payment.success", "payment.success"],
        },
    )

    assert response.status_code == 422


def test_list_webhooks(client, monkeypatch):
    token = setup_webhook_user(client)
    create_endpoint(client, token, monkeypatch)

    response = client.get(
        "/api/v1/webhooks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_deactivate_webhook(client, monkeypatch):
    token = setup_webhook_user(client)
    endpoint = create_endpoint(client, token, monkeypatch)

    response = client.post(
        f"/api/v1/webhooks/{endpoint.json()['id']}/deactivate",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_list_webhook_deliveries(client, db_session, monkeypatch):
    token, endpoint_id, delivery = setup_webhook_delivery(
        client, db_session, monkeypatch
    )

    response = client.get(
        "/api/v1/webhooks/deliveries",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["id"] == delivery.id


def test_filter_webhook_deliveries_by_status(
    client, db_session, monkeypatch
):
    token, endpoint_id, delivery = setup_webhook_delivery(
        client, db_session, monkeypatch
    )

    response = client.get(
        "/api/v1/webhooks/deliveries?status=FAILED",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = client.get(
        "/api/v1/webhooks/deliveries?status=DELIVERED",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_webhook_delivery(client, db_session, monkeypatch):
    token, endpoint_id, delivery = setup_webhook_delivery(
        client, db_session, monkeypatch
    )

    response = client.get(
        f"/api/v1/webhooks/deliveries/{delivery.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["event_id"] == delivery.event_id


def test_retry_failed_webhook(client, db_session, monkeypatch):
    token, endpoint_id, delivery = setup_webhook_delivery(
        client, db_session, monkeypatch
    )

    queued = []
    monkeypatch.setattr(
        webhook_api.deliver_webhook,
        "delay",
        lambda delivery_id: queued.append(delivery_id),
    )

    response = client.post(
        f"/api/v1/webhooks/deliveries/{delivery.id}/retry",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"
    assert queued == [delivery.id]

    db_session.refresh(delivery)
    assert delivery.status == "PENDING"
    assert delivery.attempts == 5
    assert delivery.max_attempts == 6


def test_retry_non_failed_webhook_returns_conflict(
    client, db_session, monkeypatch
):
    token = setup_webhook_user(client)
    endpoint = create_endpoint(client, token, monkeypatch)

    payment = create_payment_for_webhook(client, token)

    delivery = create_delivery(
        db_session,
        endpoint.json()["id"],
        payment["id"],
        status="DELIVERED",
    )

    response = client.post(
        f"/api/v1/webhooks/deliveries/{delivery.id}/retry",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409


def test_user_cannot_access_another_users_delivery(
    client, db_session, monkeypatch
):
    token1, endpoint_id, delivery = setup_webhook_delivery(
        client, db_session, monkeypatch
    )

    token2 = setup_webhook_user(
        client, "anotheruser@example.com"
    )

    response = client.get(
        f"/api/v1/webhooks/deliveries/{delivery.id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404

    retry_response = client.post(
        f"/api/v1/webhooks/deliveries/{delivery.id}/retry",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert retry_response.status_code == 404


def test_retry_inactive_endpoint_returns_conflict(
    client, db_session, monkeypatch
):
    token, endpoint_id, delivery = setup_webhook_delivery(
        client, db_session, monkeypatch
    )

    db_session.refresh(delivery.endpoint)
    delivery.endpoint.is_active = False
    db_session.commit()

    response = client.post(
        f"/api/v1/webhooks/deliveries/{delivery.id}/retry",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409