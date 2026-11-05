from sqlalchemy import text
from app.core.database import engine

IDEMPOTENCY_KEY = "smartpay-concurrent-db-001"

try:
    with engine.connect() as connection:
        print("\n--- Idempotency Record ---")

        record = connection.execute(
            text("""
                SELECT
                    id,
                    user_id,
                    idempotency_key,
                    payment_id,
                    status
                FROM idempotency_records
                WHERE idempotency_key = :key
            """),
            {"key": IDEMPOTENCY_KEY},
        ).mappings().first()

        if record is None:
            print("No idempotency record found.")
        else:
            print(dict(record))

            print("\n--- Linked Payment ---")

            payment_count = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM payments
                    WHERE id = :payment_id
                """),
                {"payment_id": record["payment_id"]},
            ).scalar_one()

            print("Linked payment count:", payment_count)

            if payment_count == 1:
                print("SUCCESS: Idempotency record links to one payment.")
            else:
                print("CHECK REQUIRED: Linked payment was not found.")

except Exception as error:
    print("Database verification failed:", error)