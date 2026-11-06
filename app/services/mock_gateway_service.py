
import random
from uuid import uuid4


def process_mock_payment(
    forced_status: str | None = None,
) -> dict:
    """
    Simulate a payment gateway response.

    forced_status is intended for local testing.
    If omitted, the gateway randomly chooses an outcome.
    """

    possible_statuses = [
        "SUCCESS",
        "FAILED",
        "TIMEOUT",
    ]

    if forced_status is not None:
        forced_status = forced_status.upper()

        if forced_status not in possible_statuses:
            raise ValueError(
                "Invalid gateway status. "
                "Use SUCCESS, FAILED, or TIMEOUT."
            )

        status = forced_status
    else:
        status = random.choice(possible_statuses)

    gateway_transaction_id = (
        f"GW-{uuid4().hex[:12].upper()}"
    )

    return {
        "gateway_transaction_id": gateway_transaction_id,
        "status": status,
    }
