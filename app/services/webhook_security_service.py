import hashlib
import hmac
import secrets

from cryptography.fernet import Fernet

from app.core.config import settings


def get_fernet() -> Fernet:
    """Create the Fernet encryption instance."""
    key = settings.WEBHOOK_ENCRYPTION_KEY.encode("utf-8")
    return Fernet(key)


def generate_webhook_secret() -> str:
    """Generate a unique random signing secret."""
    return secrets.token_urlsafe(32)


def encrypt_webhook_secret(secret: str) -> str:
    """Encrypt a webhook signing secret before database storage."""
    encrypted = get_fernet().encrypt(secret.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_webhook_secret(encrypted_secret: str) -> str:
    """Decrypt a stored webhook signing secret."""
    decrypted = get_fernet().decrypt(
        encrypted_secret.encode("utf-8")
    )
    return decrypted.decode("utf-8")


def generate_webhook_signature(
    payload: bytes,
    secret: str,
) -> str:
    """
    Generate an HMAC-SHA256 signature.

    The payload must be the exact bytes sent in the HTTP request.
    """
    signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return f"sha256={signature}"


def verify_webhook_signature(
    payload: bytes,
    secret: str,
    signature: str,
) -> bool:
    """Verify a received webhook signature securely."""
    expected_signature = generate_webhook_signature(
        payload=payload,
        secret=secret,
    )

    return hmac.compare_digest(
        expected_signature,
        signature,
    )