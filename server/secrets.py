from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


def _app_dir() -> Path:
    base = os.getenv("APPDATA") or str(Path.home() / ".config")
    path = Path(base) / "yumeVNGame"
    path.mkdir(parents=True, exist_ok=True)
    return path


APP_DIR = _app_dir()
MASTER_KEY_PATH = APP_DIR / "master.key"
SECRETS_PATH = APP_DIR / "secrets.enc"


def _fernet() -> Fernet:
    if not MASTER_KEY_PATH.exists():
        MASTER_KEY_PATH.write_bytes(Fernet.generate_key())
        try:
            os.chmod(MASTER_KEY_PATH, 0o600)
        except OSError:
            pass
    return Fernet(MASTER_KEY_PATH.read_bytes().strip())


def load_all() -> dict[str, Any]:
    if not SECRETS_PATH.exists():
        return {}
    try:
        raw = _fernet().decrypt(SECRETS_PATH.read_bytes())
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except (InvalidToken, json.JSONDecodeError, OSError):
        return {}


def save_all(data: dict[str, Any]) -> None:
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    SECRETS_PATH.write_bytes(_fernet().encrypt(payload))
    try:
        os.chmod(SECRETS_PATH, 0o600)
    except OSError:
        pass


def set_secret(name: str, value: str) -> None:
    data = load_all()
    data[name] = value
    save_all(data)


def get_secret(name: str) -> str | None:
    value = load_all().get(name)
    return str(value) if value else None


def delete_secret(name: str) -> None:
    data = load_all()
    data.pop(name, None)
    save_all(data)


def mask(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:4]}{'•' * 8}{value[-4:]}"


def deepseek_key() -> str | None:
    return get_secret("deepseek_api_key")


def has_deepseek_key() -> bool:
    return bool(deepseek_key())


def public_status() -> dict[str, Any]:
    key = deepseek_key()
    return {
        "has_api_key": bool(key),
        "masked_key": mask(key),
        "storage": str(SECRETS_PATH),
    }

