import ipaddress
import socket

from urllib.parse import urlsplit


def validate_webhook_url(url: str) -> None:
    """
    Validate a webhook destination to reduce SSRF risks.

    Only public HTTPS destinations on the default port are accepted.
    """

    try:
        parsed = urlsplit(url)

        if parsed.scheme.lower() != "https":
            raise ValueError("Webhook URL must use HTTPS")

        if not parsed.hostname:
            raise ValueError("Webhook URL must contain a hostname")

        if parsed.username or parsed.password:
            raise ValueError("Webhook URL cannot contain credentials")

        if parsed.fragment:
            raise ValueError("Webhook URL cannot contain a fragment")

        if parsed.port not in (None, 443):
            raise ValueError("Only HTTPS port 443 is allowed")

        hostname = parsed.hostname.lower().rstrip(".")

        if (
            hostname == "localhost"
            or hostname.endswith(".localhost")
            or hostname.endswith(".local")
        ):
            raise ValueError("Local webhook destinations are not allowed")

        try:
            addresses = [ipaddress.ip_address(hostname)]
        except ValueError:
            results = socket.getaddrinfo(
                hostname,
                443,
                type=socket.SOCK_STREAM,
            )

            addresses = [
                ipaddress.ip_address(result[4][0])
                for result in results
            ]

        if not addresses:
            raise ValueError("Webhook hostname did not resolve")

        if any(not address.is_global for address in addresses):
            raise ValueError(
                "Webhook destination must resolve only to public IP addresses"
            )

    except ValueError:
        raise

    except OSError as exc:
        raise ValueError(
            "Webhook hostname could not be resolved"
        ) from exc