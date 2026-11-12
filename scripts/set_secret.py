from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from server import db, secrets


def main() -> None:
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set DEEPSEEK_API_KEY in the environment first.")
    secrets.set_secret("deepseek_api_key", key)
    db.set_settings(
        {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        }
    )
    print(f"Stored encrypted key at {secrets.SECRETS_PATH}")
    print("The key is not written to the repository.")


if __name__ == "__main__":
    main()

