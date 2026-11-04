
import hashlib
import json
import uuid

from app.core.redis import redis_client


IDEMPOTENCY_TTL_SECONDS = 86400
PROCESSING_TTL_SECONDS = 120


def generate_request_fingerprint(user_id: int, payment_data) -> str:
    """
    Generate a consistent fingerprint for payment details.
    """

    request_data = {
        "user_id": user_id,
        "amount": str(payment_data.amount),
        "currency": payment_data.currency.upper(),
        "payment_method": payment_data.payment_method.value,
    }

    serialized_data = json.dumps(request_data, sort_keys=True)

    return hashlib.sha256(
        serialized_data.encode("utf-8")
    ).hexdigest()


def get_idempotency_key(user_id: int, idempotency_key: str) -> str:
    """
    Generate a Redis key scoped to the user.
    """

    return f"idempotency:user_{user_id}:{idempotency_key}"


def get_idempotency_record(redis_key: str):
    """
    Retrieve an existing idempotency record.
    """

    record = redis_client.get(redis_key)

    if record is None:
        return None

    return json.loads(record)


def reserve_idempotency_key(redis_key: str):
    """
    Atomically reserve an idempotency key.

    Returns a unique reservation token if successful.
    Returns None if another request already owns the key.
    """

    reservation_token = str(uuid.uuid4())

    reservation = {
        "status": "PROCESSING",
        "reservation_token": reservation_token,
    }

    reserved = redis_client.set(
        redis_key,
        json.dumps(reservation),
        ex=PROCESSING_TTL_SECONDS,
        nx=True,
    )

    if reserved:
        return reservation_token

    return None


def store_idempotency_record(
    redis_key: str,
    request_fingerprint: str,
    payment_id: int,
    reservation_token: str,
) -> bool:
    """
    Complete a reservation only when its token matches.

    The Lua script checks ownership and stores the completed record
    atomically, preventing another request from overwriting it.
    """

    record = {
        "status": "COMPLETED",
        "request_fingerprint": request_fingerprint,
        "payment_id": payment_id,
    }

    script = """
    local current = redis.call('GET', KEYS[1])

    if not current then
        return 0
    end

    local decoded = cjson.decode(current)

    if decoded['status'] ~= 'PROCESSING' then
        return 0
    end

    if decoded['reservation_token'] ~= ARGV[1] then
        return 0
    end

    redis.call('SET', KEYS[1], ARGV[2], 'EX', ARGV[3])

    return 1
    """

    result = redis_client.eval(
        script,
        1,
        redis_key,
        reservation_token,
        json.dumps(record),
        IDEMPOTENCY_TTL_SECONDS,
    )

    return bool(result)


def release_idempotency_reservation(
    redis_key: str,
    reservation_token: str,
) -> bool:
    """
    Release a reservation only if this request owns it.
    """

    script = """
    local current = redis.call('GET', KEYS[1])

    if not current then
        return 0
    end

    local decoded = cjson.decode(current)

    if decoded['status'] == 'PROCESSING'
       and decoded['reservation_token'] == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    end

    return 0
    """

    result = redis_client.eval(
        script,
        1,
        redis_key,
        reservation_token,
    )

    return bool(result)
