import time

from app.core.redis import redis_client


VELOCITY_WINDOW_SECONDS = 300


def record_transaction_and_count(
    user_id: int,
    transaction_id: str,
) -> int:
    """
    Record a transaction in Redis and count the
    user's unique transactions within five minutes.
    """

    key = f"fraud:attempts:user_{user_id}"

    current_time = time.time()
    window_start = current_time - VELOCITY_WINDOW_SECONDS

    # Execute all Redis operations atomically.
    pipeline = redis_client.pipeline(transaction=True)

    # Remove transactions older than five minutes.
    pipeline.zremrangebyscore(
        key,
        "-inf",
        window_start,
    )

    # Record the current transaction.
    pipeline.zadd(
       key,
       {transaction_id: current_time},
       nx=True,
    )

    # Count transactions in the five-minute window.
    pipeline.zcard(key)

    # Automatically expire inactive counters.
    pipeline.expire(
        key,
        VELOCITY_WINDOW_SECONDS,
    )

    results = pipeline.execute()

    transaction_count = results[2]

    return transaction_count