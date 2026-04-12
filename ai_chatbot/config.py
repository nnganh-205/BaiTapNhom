import os
from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    """Load project-local .env first, then let shell vars override when present."""
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
    else:
        # Also support launching from repository root where .env may be configured.
        load_dotenv(override=False)


def has_google_api_key() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY", "").strip())

