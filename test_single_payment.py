import getpass
import uuid
import httpx

token = getpass.getpass("Paste your raw access token: ").strip()

headers = {
    "Authorization": f"Bearer {token}",
    "Idempotency-Key": f"single-test-{uuid.uuid4().hex}",
}

payment_data = {
    "amount": 750,
    "currency": "INR",
    "payment_method": "UPI",
}

with httpx.Client(
    timeout=30.0,
    trust_env=False,
) as client:

    # First check basic connectivity.
    health = client.get("http://127.0.0.1:8000/docs")
    print("Swagger HTTP Status:", health.status_code)

    # Then submit one payment.
    response = client.post(
        "http://127.0.0.1:8000/api/v1/payments/create",
        headers=headers,
        json=payment_data,
    )

    print("Payment HTTP Status:", response.status_code)
    print("Payment Response:", response.text)