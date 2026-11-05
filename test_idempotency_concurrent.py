import os
import threading
from concurrent.futures import ThreadPoolExecutor

import httpx


BASE_URL = "http://127.0.0.1:8000"

TOKEN = os.environ["SMARTPAY_TEST_TOKEN"]

IDEMPOTENCY_KEY = "smartpay-concurrent-db-001"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Idempotency-Key": IDEMPOTENCY_KEY,
}

PAYLOAD = {
    "amount": 1200,
    "currency": "INR",
    "payment_method": "UPI",
}

barrier = threading.Barrier(2)


def send_payment():
    with httpx.Client(timeout=30) as client:
        barrier.wait()

        response = client.post(
            f"{BASE_URL}/api/v1/payments/create",
            headers=HEADERS,
            json=PAYLOAD,
        )

        return response.status_code, response.json()


with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [
        executor.submit(send_payment),
        executor.submit(send_payment),
    ]

    results = [future.result() for future in futures]


payment_ids = set()

for index, (status_code, body) in enumerate(results, start=1):
    print(f"\nRequest {index}")
    print("HTTP Status:", status_code)
    print("Response:", body)

    if status_code in (200, 201):
        payment_ids.add(body["id"])

print("\nUnique payment IDs:", payment_ids)
print("Number of unique payments:", len(payment_ids))

if (
    all(status in (200, 201) for status, _ in results)
    and len(payment_ids) == 1
):
    print("\nSUCCESS: No duplicate payment was created.")
else:
    print("\nCHECK REQUIRED: Unexpected concurrent result.")