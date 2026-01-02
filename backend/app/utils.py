import secrets
import string


def generate_token(length: int = 8) -> str:
    """Generate a random alphanumeric token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_tracking_url(token: str, base_url: str = "https://track.kaskyralmaty.dev") -> str:
    """Generate tracking URL for client."""
    return f"{base_url}/?t={token}"
