import random
from uuid import uuid4


def process_mock_payment() -> dict:
    """
    Simulate a payment gateway response.

    This is only for local educational/testing purposes.
    No real money or banking system is involved.
    """

    possible_statuses = [
        "SUCCESS",
        "FAILED",
        "TIMEOUT",
    ]

    status = random.choice(possible_statuses)

    gateway_transaction_id = f"GW-{uuid4().hex[:12].upper()}"

    return {
        "gateway_transaction_id": gateway_transaction_id,
        "status": status,
    }